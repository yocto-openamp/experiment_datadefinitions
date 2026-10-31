import pathlib
import re
import subprocess

import pytest

from experiment_datadefinitions.datamodel import unittests_simple
from experiment_datadefinitions.renderer import renderer_cpp

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent
DIRECTORY_SRC_CPP = DIRECTORY_OF_THIS_FILE / "src_cpp"


def test_src_cpp() -> None:
    model = unittests_simple.ModelPidController(name="Axis W", value=42, i_param=3.14)
    renderer = renderer_cpp.RendererCPP(model=model)

    def generate_compile() -> None:
        """
        TODO: Clearer interface
        """
        def generate(filename: pathlib.Path, source: str) -> None:
            filename.write_text(source)

        generate(
            DIRECTORY_SRC_CPP / "generated_pid_controller_struct.hpp",
            renderer.render_cpp_struct(),
        )
        generate(
            DIRECTORY_SRC_CPP / "generated_pid_controller_initializer.hpp",
            renderer.render_cpp_initializer(),
        )

        subprocess.run(
            ["g++", "-Wall", "-Wextra", "dump_values.cpp", "-o", "dump_values"],
            cwd=DIRECTORY_SRC_CPP,
            check=True,
        )

    def run() -> bytes:
        """
        TODO: Clearer interface
        """
        result = subprocess.run(
            ["./dump_values"],
            cwd=DIRECTORY_SRC_CPP,
            check=True,
            capture_output=True,
            text=True,
        )

        stdout = result.stdout.strip()
        match = re.fullmatch(r">0x(?P<hexstring>[0-9A-F]+)<", stdout)
        assert match is not None
        hexstring = match.group("hexstring")
        serialized = bytes.fromhex(hexstring)
        return serialized

    generate_compile()
    serialized = run()

    model3 = renderer.deserialize_from_cpp(serizalized=serialized)
    assert isinstance(model3, unittests_simple.ModelPidController)
    assert model3.name == model.name
    assert model3.value == model.value
    assert model3.i_param == pytest.approx(model.i_param, rel=1e-6)
    assert len(serialized) == 40
