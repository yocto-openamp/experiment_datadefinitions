from pydantic import BaseModel


class ModelPidController(BaseModel):
    name: str
    value: int

