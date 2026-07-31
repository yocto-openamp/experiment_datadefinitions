import pydantic

from utils.util_pydantic import SchemaExtra

from . import unittests_simple


class ModelSystemDual(pydantic.BaseModel):
    first: unittests_simple.ModelPidController = pydantic.Field(
        default_factory=unittests_simple.ModelPidController,
    )
    second: unittests_simple.ModelPidController = pydantic.Field(
        default_factory=unittests_simple.ModelPidController,
    )


class ModelSystemList(pydantic.BaseModel):
    controllers: list[unittests_simple.ModelPidController] = pydantic.Field(
        min_length=2,
        max_length=2,
        default_factory=list,
    )
    debuglevel: int = pydantic.Field(
        default=4095,
        ge=0,
        le=4,
        json_schema_extra=SchemaExtra(
            unit="1",
            comment="0: off, 1: debug, 2: info, 3: warn, 4: error",
        ).dict,
    )
