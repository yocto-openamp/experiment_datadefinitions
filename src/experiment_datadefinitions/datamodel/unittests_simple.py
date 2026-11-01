import typing

import pydantic

from experiment_datadefinitions.utils.util_pydantic import SchemaExtra


class ModelPidController(pydantic.BaseModel):
    cpp_filename: typing.ClassVar[str] = "pid_controller"
    """
    Used to name the generated files, e.g. generated_pid_controller_struct.hpp
    """

    name: str = pydantic.Field(
        default="AxisXYZ",
        json_schema_extra=SchemaExtra(
            comment="Name of the controlled axis",
        ).dict,
    )
    value: int = pydantic.Field(
        default=4095,
        ge=-4095,
        le=4095,
        json_schema_extra=SchemaExtra(
            unit="steps (4096 steps = 1 revolution)",
            comment="Encoder steps",
            cpp_type="uint16_t",
        ).dict,
    )
    i_param: float = pydantic.Field(
        default=0.25,
        json_schema_extra=SchemaExtra(
            unit="s",
            comment="Integral gain (I) of the PID controller",
        ).dict,
    )
