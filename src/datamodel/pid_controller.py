from pydantic import BaseModel, Field


class ModelPidController(BaseModel):
    name: str = Field(
        default="AxisX",
        json_schema_extra={
            "Comment": "Name of the controlled axis",
        },
    )
    value: int = Field(
        default=4095,
        ge=0,
        le=4294967295,
        json_schema_extra={
            "Unit": "steps (4096 steps = 1 revolution)",
            "Comment": "Encoder steps.",
        },
    )
    i_param: float = Field(
        default=0.25,
        json_schema_extra={
            "Unit": "s",
            "Comment": "Integral gain (I) of the PID controller",
        },
    )
