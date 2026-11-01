
import typing

import pydantic
import pytest

from experiment_datadefinitions.datamodel import unittests_simple
from experiment_datadefinitions.renderer import renderer_cpp
from experiment_datadefinitions.utils import util_pydantic
from experiment_datadefinitions.utils.util_pydantic import SchemaExtra


def test_datamodel_fields_are_set() -> None:
    model = unittests_simple.ModelPidController(name="Axis Z", value=42, i_param=3.14)

    assert model.name == "Axis Z"
    assert model.value == 42
    assert model.i_param == 3.14


EXPECTED_CPP_STRUCT = """
typedef struct __attribute__((packed)) {
    // Name of the controlled axis
    char name[32];
    // [steps (4096 steps = 1 revolution)] Encoder steps
    uint16_t value;
    // [s] Integral gain (I) of the PID controller
    float i_param;
} ModelPidController_t;
"""

EXPECTED_CPP_INITIALIZER = """
static const ModelPidController_t pid_controller = {
    "Axis W",
    42,
    3.14
};
"""


def test_renderer_cpp() -> None:
    model = unittests_simple.ModelPidController(name="Axis W", value=42, i_param=3.14)
    renderer = renderer_cpp.RendererCPP(model=model)

    cpp_struct = renderer.render_cpp_struct()
    assert cpp_struct == EXPECTED_CPP_STRUCT

    cpp_initializer = renderer.render_cpp_initializer()
    assert cpp_initializer == EXPECTED_CPP_INITIALIZER

    model2 = unittests_simple.ModelPidController(name="sensor", value=43, i_param=3.141)
    serialized = renderer.serialize_to_cpp(model=model2)

    decoded = renderer.ctypes_model.from_buffer_copy(serialized)
    assert decoded.name.split(b"\0", 1)[0] == b"sensor"
    assert decoded.value == 43
    assert decoded.i_param == pytest.approx(3.141, rel=1e-6)

    model3 = renderer.deserialize_from_cpp(serizalized=serialized)
    assert isinstance(model3, unittests_simple.ModelPidController)
    assert model3.name == model2.name
    assert model3.value == model2.value
    assert model3.i_param == pytest.approx(model2.i_param, rel=1e-6)


def test_renderer_cpp_missing_cpp_filename() -> None:
    class ModelWithoutFilename(pydantic.BaseModel):
        value: int = 1

    renderer = renderer_cpp.RendererCPP(model=ModelWithoutFilename())

    with pytest.raises(ValueError, match="'ModelWithoutFilename' has no 'cpp_filename'"):
        _ = renderer.filename_struct


def test_field_limits() -> None:
    class ModelLimits(pydantic.BaseModel):
        limited: int = pydantic.Field(default=1, ge=-2, le=3)
        unlimited: int = 1
        only_ge: int = pydantic.Field(default=1, ge=0)

    fields = {
        field.field_name: field
        for field in util_pydantic.FieldInfoIter.iter_model(ModelLimits())
    }
    assert (fields["limited"].minimum, fields["limited"].maximum) == (-2, 3)
    assert (fields["unlimited"].minimum, fields["unlimited"].maximum) == (None, None)
    assert (fields["only_ge"].minimum, fields["only_ge"].maximum) == (0, None)


EXPECTED_CPP_STRUCT_TYPES = """
typedef struct __attribute__((packed)) {
    int16_t value_int16;
    int32_t value_int32;
    uint64_t value_uint64;
    double value_double;
} ModelTypes_t;
"""


def test_renderer_cpp_types() -> None:
    def field(default: float, cpp_type: str) -> typing.Any:
        return pydantic.Field(
            default=default,
            json_schema_extra=SchemaExtra(cpp_type=cpp_type).dict,
        )

    class ModelTypes(pydantic.BaseModel):
        value_int16: int = field(-32768, "int16_t")
        value_int32: int = field(-2147483648, "int32_t")
        value_uint64: int = field(2**64 - 1, "uint64_t")
        value_double: float = field(1 / 3, "double")

    model = ModelTypes()
    renderer = renderer_cpp.RendererCPP(model=model)
    assert renderer.render_cpp_struct() == EXPECTED_CPP_STRUCT_TYPES

    serialized = renderer.serialize_to_cpp(model=model)
    assert len(serialized) == 22
    assert renderer.deserialize_from_cpp(serizalized=serialized) == model

