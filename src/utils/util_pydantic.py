from __future__ import annotations

import dataclasses
import logging
import typing

import pydantic

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
