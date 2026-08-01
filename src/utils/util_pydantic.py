from __future__ import annotations

import dataclasses
import logging
import typing

import annotated_types
import pydantic

from utils import util_pydantic

logger = logging.getLogger(__file__)


@dataclasses.dataclass(frozen=True)
class FieldInfoIter:
    field_name: str
    field_info: pydantic.fields.FieldInfo

    @property
    def title(self) -> str:
        return self.field_info.title or self.field_name.replace("_", " ").title()

    @property
    def schema_extra(self) -> SchemaExtra:
        try:
            assert isinstance(self.field_info.json_schema_extra, dict)
            extra = SchemaExtra(**self.field_info.json_schema_extra)
            return extra
        except Exception as e:
            logger.error(f"Field '{self.field_name}': {e}!")
            return SchemaExtra()

    @staticmethod
    def iter_model(model: type[pydantic.BaseModel]) -> typing.Iterator[FieldInfoIter]:
        assert issubclass(model, pydantic.BaseModel)
        for field_name, field_info in model.model_fields.items():
            yield FieldInfoIter(field_name=field_name, field_info=field_info)


@dataclasses.dataclass(frozen=True)
class SchemaExtra:
    unit: str = ""
    """
    Examples: m, V, step
    """

    comment: str = ""
    """
    Examples: Encoder steps
    """

    @property
    def dict(self) -> dict[str, typing.Any]:
        return dataclasses.asdict(self)


class ModelHierarchy(dict[str, util_pydantic.FieldInfoIter]):
    @staticmethod
    def factory(model: pydantic.BaseModel) -> ModelHierarchy:
        mh = ModelHierarchy()

        def walk_model_paths(model: pydantic.BaseModel, prefix: str = "") -> None:
            assert issubclass(model, pydantic.BaseModel)

            for field in util_pydantic.FieldInfoIter.iter_model(model):
                path = f"{prefix}/{field.field_name}"
                annotation = field.field_info.annotation
                if (annotation is list) or (typing.get_origin(annotation) is list):

                    def get_annotation[T: annotated_types.BaseMetadata](
                        annotated_type: type[T],
                    ) -> T:
                        for j in field.field_info.metadata:
                            if isinstance(j, annotated_type):
                                return j
                        raise NotImplementedError()

                    min_length = get_annotation(annotated_types.MinLen).min_length
                    max_length = get_annotation(annotated_types.MaxLen).max_length
                    assert min_length == max_length
                    (item_type,) = typing.get_args(
                        annotation
                    )  # -> datamodel.unittests_simple.ModelPidController
                    for i in range(min_length):
                        walk_model_paths(item_type, f"{path}/{i}")
                    continue
                if issubclass(field.field_info.annotation, pydantic.BaseModel):
                    walk_model_paths(field.field_info.annotation, path)
                    continue
                mh[path] = field

        walk_model_paths(model=model)

        return mh

    def dump(self):
        for path, item in self.items():
            print(f"{path}: ...")
