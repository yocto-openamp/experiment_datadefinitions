from datamodel import pid_controller


def test_datamodel_fields_are_set() -> None:
    model = pid_controller.ModelPidController(name="sensor", value=42)

    assert model.name == "sensor"
    assert model.value == 42
