from pydantic import BaseModel, Field


class ModelPidController(BaseModel):
    name: str = Field(
        json_schema_extra={
            "Comment": "Name of the controlled axis",
        },
    )
    value: int = Field(
        ge=0,
        le=4294967295,
        json_schema_extra={
            "Unit": "steps (4096 steps = 1 revolution)",
            "Comment": "Encoder steps.",
        },
    )
    i_param: float = Field(
        json_schema_extra={
            "Unit": "V",
            "Comment": "Integral gain (I) of the PID controller",
        }
    )
