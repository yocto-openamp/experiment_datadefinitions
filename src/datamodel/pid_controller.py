from pydantic import BaseModel, Field


class ModelPidController(BaseModel):
    name: str
    value: int = Field(
        ge=0,
        le=4294967295,
        json_schema_extra={"Unit": "steps"},
    )
    i_param: float = Field(
        json_schema_extra={
            "Unit": "V",
            "Comment": "The integral I param for the controller",
        }
    )
