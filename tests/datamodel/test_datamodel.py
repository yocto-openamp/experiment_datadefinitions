
from experiment_datadefinitions.datamodel import unittests_simple
from experiment_datadefinitions.renderer import renderer_cpp


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
    uint32_t value;
    // [s] Integral gain (I) of the PID controller
    double i_param;
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
    assert decoded.i_param == 3.141

    model3 = renderer.deserialize_from_cpp(serizalized=serialized)
    assert isinstance(model3, unittests_simple.ModelPidController)
    assert model3.name == model2.name
    assert model3.value == model2.value
    assert model3.i_param == model2.i_param

