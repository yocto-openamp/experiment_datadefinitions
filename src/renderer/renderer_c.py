import ctypes
from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class TypeSourceC:
    """
    This is the mapping of the python datatype to the C code.
    """

    c_source: str
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
        return bytes(value).split(b"\0", 1)[0].decode("utf-8")

    @staticmethod
    def to_c_literal(value: object) -> str:
        if isinstance(value, str):
            return f'"{value}"'
        return str(value)


class RendererC:
    """Render a simple C struct definition from a Pydantic model."""

    _TYPE_MAP = {
        str: TypeSourceC(
            c_source="char {name}[32];",
            ctypes_type=ctypes.c_char * 32,
            to_ctypes=lambda value: value.encode("utf-8"),
            from_ctypes=TypeSourceC.decode_c_string,
        ),
        int: TypeSourceC(
            c_source="uint32_t {name};",
            ctypes_type=ctypes.c_uint32,
            to_ctypes=lambda value: ctypes.c_uint32(int(value)),
            from_ctypes=lambda value: int(value),
        ),
        float: TypeSourceC(
            c_source="double {name};",
            ctypes_type=ctypes.c_double,
            to_ctypes=lambda value: ctypes.c_double(float(value)),
            from_ctypes=lambda value: float(value),
        ),
    }

    def __init__(self, model: BaseModel) -> None:
        self.model = model
        self.ctypes_model = self._create_ctypes_model()

    def render_c_struct(self) -> str:
        """
        Render 'self.model' into something like:

            typedef struct
            {
                char name[32];
                uint32_t value;
                double i_param;
            } ModelPidController_t;
        """
        lines = ["", "typedef struct", "{"]

        for field_name, field_info in type(self.model).model_fields.items():
            annotation = field_info.annotation
            if annotation not in self._TYPE_MAP:
                raise ValueError(
                    f"Unsupported field type for '{field_name}': {annotation}"
                )

            json_schema_extra = field_info.json_schema_extra or {}
            comment = self._render_comment(
                field_name=field_name, extra=json_schema_extra,
            )
            if comment:
                lines.append(f"    // {comment}")

            c_decl = self._TYPE_MAP[annotation].c_source.format(name=field_name)
            lines.append(f"    {c_decl}")

        struct_name = type(self.model).__name__
        lines.extend([f"}} {struct_name}_t;", ""])
        return "\n".join(lines)

    def render_c_initializer(self) -> str:
        struct_name = type(self.model).__name__
        var_name = self._model_var_name(struct_name)

        lines = ["", f"static const {struct_name}_t {var_name} = {{"]

        for field_name, field_info in type(self.model).model_fields.items():
            annotation = field_info.annotation
            if annotation not in self._TYPE_MAP:
                raise ValueError(
                    f"Unsupported field type for '{field_name}': {annotation}"
                )

            json_schema_extra = field_info.json_schema_extra or {}
            c_init_value = json_schema_extra.get("CInitValue")
            if c_init_value is None:
                if field_info.is_required():
                    raise ValueError(
                        f"Field '{field_name}' is required and has no default/CInitValue"
                    )
                c_init_value = TypeSourceC.to_c_literal(field_info.default)

            lines.append(f"    {c_init_value},")

        if len(lines) > 2:
            lines[-1] = lines[-1].rstrip(",")

        lines.extend(["};", ""])
        return "\n".join(lines)

    def serialize_to_c(self, model: BaseModel) -> bytes:
        assert type(self.model) is type(model)
        instance = self.ctypes_model()
        for field_name, field_info in type(self.model).model_fields.items():
            value = getattr(model, field_name)
            type_source = self._type_source_for_annotation(field_info.annotation)
            setattr(
                instance,
                field_name,
                type_source.to_ctypes(value),
            )

        return bytes(instance)

    def deserialize_from_c(self, serizalized: bytes) -> BaseModel:
        instance = self.ctypes_model.from_buffer_copy(serizalized)
        model_data = {}

        for field_name, field_info in type(self.model).model_fields.items():
            raw_value = getattr(instance, field_name)
            type_source = self._type_source_for_annotation(field_info.annotation)
            model_data[field_name] = type_source.from_ctypes(raw_value)

        model_type = type(self.model)
        return model_type(**model_data)

    @staticmethod
    def _render_comment(field_name: str, extra: dict) -> str:
        comment = extra.get("Comment", "")
        unit = extra.get("Unit", "")

        if field_name == "value":
            if "4096 steps = 1 revolution" in unit:
                comment = "4096 steps per revolution"

        if unit:
            return f"[{unit}] {comment}".rstrip()

        return comment

    @staticmethod
    def _model_var_name(model_name: str) -> str:
        core_name = model_name[5:] if model_name.startswith("Model") else model_name
        chars: list[str] = []
        for index, char in enumerate(core_name):
            if char.isupper() and index > 0:
                chars.append("_")
            chars.append(char.lower())
        return "".join(chars)

    def _create_ctypes_model(self) -> type[ctypes.Structure]:
        """
        Create the ctypes structure matching the C layout of the model.
        """
        fields = []
        for field_name, field_info in type(self.model).model_fields.items():
            annotation = field_info.annotation
            ctypes_type = self._type_source_for_annotation(annotation).ctypes_type
            fields.append((field_name, ctypes_type))

        class SerializedModel(ctypes.Structure):
            _fields_ = fields

        return SerializedModel


    @classmethod
    def _type_source_for_annotation(cls, annotation: object) -> TypeSourceC:
        if annotation not in cls._TYPE_MAP:
            raise ValueError(f"Unsupported field type for serialization: {annotation}")
        return cls._TYPE_MAP[annotation]
