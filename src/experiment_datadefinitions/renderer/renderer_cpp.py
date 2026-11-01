from __future__ import annotations

import ctypes
import typing
from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel

from experiment_datadefinitions.utils.util_pydantic import FieldInfoIter


@dataclass(frozen=True)
class TypeSourceCPP:
    """
    This is the mapping of the python datatype to the C code.
    """

    cpp_source: str
    """
    Example: "int32", "const char*", "float"
    """

    ctypes_type: type[ctypes._SimpleCData] | type[ctypes.Array]
    """
    ctypes....
    """

    to_ctypes: Callable[[object], object]
    from_ctypes: Callable[[object], object]

    @staticmethod
    def decode_c_string(value: object) -> str:
        if isinstance(value, bytes):
            return value.split(b"\0", 1)[0].decode("utf-8")
        return bytes(value).split(b"\0", 1)[0].decode("utf-8")  # type: ignore[call-overload]

    @staticmethod
    def to_c_literal(value: object) -> str:
        if isinstance(value, str):
            return f'"{value}"'
        return str(value)


class TypeMapCPP(dict[type, TypeSourceCPP]):
    def get2(self, type_var: typing.Any) -> TypeSourceCPP:
        return self[type_var]


TYPE_MAP_CPP = TypeMapCPP(
    {
        str: TypeSourceCPP(
            cpp_source="char {name}[32];",
            ctypes_type=ctypes.c_char * 32,
            to_ctypes=lambda value: value.encode("utf-8"),  # type: ignore[attr-defined]
            from_ctypes=TypeSourceCPP.decode_c_string,
        ),
        int: TypeSourceCPP(
            cpp_source="uint32_t {name};",
            ctypes_type=ctypes.c_uint32,
            to_ctypes=lambda value: ctypes.c_uint32(int(value)),  # type: ignore[call-overload]
            from_ctypes=lambda value: int(value),  # type: ignore[call-overload]
        ),
        float: TypeSourceCPP(
            cpp_source="float {name};",
            ctypes_type=ctypes.c_float,
            to_ctypes=lambda value: ctypes.c_float(float(value)),  # type: ignore[attr-defined,arg-type]
            from_ctypes=lambda value: float(value),  # type: ignore[arg-type]
        ),
    }
)


class RendererCPP:
    """Render a simple C struct definition from a Pydantic model."""

    def __init__(self, model: BaseModel) -> None:
        self.model = model
        self.ctypes_model = self._create_ctypes_model(self.model)

    def render_cpp_struct(self) -> str:
        """
        Render 'self.model' into something like:

            typedef struct __attribute__((packed)) {
                char name[32];
                uint32_t value;
                float i_param;
            } ModelPidController_t;

        Nested models are only referenced: Their struct has to be defined upfront.
        """
        lines = ["", "typedef struct __attribute__((packed)) {"]

        for field in FieldInfoIter.iter_model(self.model):
            annotation = field.field_info.annotation
            if self._is_nested_model(annotation):
                cpp_decl = f"{field.value_type_name}_t {field.field_name};"
            elif annotation in TYPE_MAP_CPP:
                cpp_decl = TYPE_MAP_CPP.get2(annotation).cpp_source.format(name=field.field_name)
            else:
                raise ValueError(
                    f"Unsupported field type for '{field.field_name}': {annotation}"
                )

            comment = self._render_comment(field)
            if comment:
                lines.append(f"    // {comment}")

            lines.append(f"    {cpp_decl}")

        struct_name = type(self.model).__name__
        lines.extend([f"}} {struct_name}_t;", ""])
        return "\n".join(lines)

    def render_cpp_initializer(self) -> str:
        """
        Nested models are only referenced: Their variable has to be defined upfront.
        """
        struct_name = type(self.model).__name__
        var_name = self._model_var_name(struct_name)

        lines = ["", f"static const {struct_name}_t {var_name} = {{"]

        for field in FieldInfoIter.iter_model(self.model):
            if self._is_nested_model(field.value_type):
                lines.append(f"    {self._model_var_name(field.value_type_name)},")
                continue

            if field.value_type not in TYPE_MAP_CPP:
                raise ValueError(
                    f"Unsupported field type for '{field.field_name}': {field.value_type_name}"
                )

            cpp_init_value = field.schema.get("CPPInitValue")
            if cpp_init_value is None:
                if field.field_info.is_required():
                    raise ValueError(
                        f"Field '{field.field_name}' is required and has no default/CPPInitValue"
                    )
                cpp_init_value = TypeSourceCPP.to_c_literal(field.get_value())

            lines.append(f"    {cpp_init_value},")

        if len(lines) > 2:
            lines[-1] = lines[-1].rstrip(",")

        lines.extend(["};", ""])
        return "\n".join(lines)

    def serialize_to_cpp(self, model: BaseModel) -> bytes:
        assert type(self.model) is type(model)
        instance = self.ctypes_model()
        self._model_to_ctypes(model, instance)
        return bytes(instance)

    def _model_to_ctypes(self, model: BaseModel, instance: ctypes.Structure) -> None:
        for field in FieldInfoIter.iter_model(model):
            value = field.get_value()
            annotation = field.field_info.annotation
            if self._is_nested_model(annotation):
                # Accessing a nested ctypes structure returns a view into 'instance'
                self._model_to_ctypes(value, getattr(instance, field.field_name))
                continue

            type_source = self._type_source_for_annotation(annotation)
            setattr(
                instance,
                field.field_name,
                type_source.to_ctypes(value),
            )

    def deserialize_from_cpp(self, serizalized: bytes) -> BaseModel:
        instance = self.ctypes_model.from_buffer_copy(serizalized)
        return self._model_from_ctypes(self.model, instance)

    def _model_from_ctypes(self, model: BaseModel, instance: ctypes.Structure) -> BaseModel:
        model_data: dict[str, typing.Any] = {}

        for field in FieldInfoIter.iter_model(model):
            raw_value = getattr(instance, field.field_name)
            annotation = field.field_info.annotation
            if self._is_nested_model(annotation):
                model_data[field.field_name] = self._model_from_ctypes(field.get_value(), raw_value)
                continue

            type_source = self._type_source_for_annotation(annotation)
            model_data[field.field_name] = type_source.from_ctypes(raw_value)

        model_type = type(model)
        return model_type(**model_data)

    @staticmethod
    def _is_nested_model(annotation: object) -> bool:
        return isinstance(annotation, type) and issubclass(annotation, BaseModel)

    @staticmethod
    def _render_comment(field: FieldInfoIter) -> str:
        extra = field.schema_extra

        if extra.unit:
            return f"[{extra.unit}] {extra.comment}".strip()

        return extra.comment

    @staticmethod
    def _model_var_name(model_name: str) -> str:
        core_name = model_name[5:] if model_name.startswith("Model") else model_name
        chars: list[str] = []
        for index, char in enumerate(core_name):
            if char.isupper() and index > 0:
                chars.append("_")
            chars.append(char.lower())
        return "".join(chars)

    def _create_ctypes_model(self, model: BaseModel) -> type[ctypes.Structure]:
        """
        Create the ctypes structure matching the packed C layout of the model.
        """
        fields: list[tuple[str, typing.Any]] = []
        for field in FieldInfoIter.iter_model(model):
            annotation = field.field_info.annotation
            if self._is_nested_model(annotation):
                fields.append((field.field_name, self._create_ctypes_model(field.get_value())))
                continue

            ctypes_type = self._type_source_for_annotation(annotation).ctypes_type
            fields.append((field.field_name, ctypes_type))

        class SerializedModel(ctypes.Structure):
            # python >= 3.14 deprecates '_pack_' without '_layout_' on non-windows
            _layout_ = "ms"
            _pack_ = 1
            _fields_ = fields

        return SerializedModel

    @classmethod
    def _type_source_for_annotation(cls, annotation: object) -> TypeSourceCPP:
        if annotation not in TYPE_MAP_CPP:
            raise ValueError(f"Unsupported field type for serialization: {annotation}")
        return TYPE_MAP_CPP.get2(annotation)
