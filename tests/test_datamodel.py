from datamodel import pid_controller
from renderer import renderer_c


def test_datamodel_fields_are_set() -> None:
    model = pid_controller.ModelPidController(name="sensor", value=42, i_param=3.14)

    assert model.name == "sensor"
    assert model.value == 42
    assert model.i_param == 3.14


EXPECTED_C_STRUCT = """
typedef struct
{
    char name[65];      // Up to 64 characters + null terminator
    uint32_t value;     // Unsigned 32-bit integer
    double i_param;     // Double-precision floating-point
} MyStruct;
"""


def test_renderer_c() -> None:
    model = pid_controller.ModelPidController(name="sensor", value=42, i_param=3.14)
    renderer = renderer_c.RendererC(model=model)
    c_struct = renderer.render_c_struct()
    assert c_struct == EXPECTED_C_STRUCT
