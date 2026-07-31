"""NiceGUI application scaffold for the PID controller model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fastapi import FastAPI
from nicegui import ui

from datamodel.pid_controller import ModelPidController

fastapi_app = FastAPI()
app = fastapi_app


@dataclass
class WebUIState:
    model: ModelPidController = field(default_factory=ModelPidController)


def _create_text_field(state: WebUIState, name: str, title: str) -> None:
    ui.input(label=title, value=getattr(state.model, name)).bind_value(state.model, name)


def _create_integer_field(state: WebUIState, name: str, title: str, schema: dict[str, Any]) -> None:
    ui.number(
        label=title,
        value=getattr(state.model, name),
        min=schema.get("minimum"),
        max=schema.get("maximum"),
        step=1,
    ).bind_value(state.model, name)


def _create_float_field(state: WebUIState, name: str, title: str, schema: dict[str, Any]) -> None:
    ui.number(
        label=title,
        value=getattr(state.model, name),
        min=schema.get("minimum"),
        max=schema.get("maximum"),
        step=0.1,
    ).bind_value(state.model, name)


def create_app(state: WebUIState | None = None) -> WebUIState:
    """Build the NiceGUI screen for the PID controller model."""
    state = state or WebUIState()
    schema = state.model.model_json_schema()
    properties = schema.get("properties", {})

    with ui.column().classes("w-full max-w-2xl gap-4 p-4"):
        ui.label("PID Controller").classes("text-2xl font-bold")
        ui.label("Edit the model fields below.").classes("text-sm text-gray-600")

        for name, field_schema in properties.items():
            title = field_schema.get("title", name)
            field_type = field_schema.get("type")

            if field_type == "string":
                _create_text_field(state, name, title)
            elif field_type == "integer":
                _create_integer_field(state, name, title, field_schema)
            elif field_type == "number":
                _create_float_field(state, name, title, field_schema)
            else:
                ui.label(f"{title}: unsupported field type {field_type!r}")

        ui.separator()
        ui.label("Current model state").classes("text-lg font-semibold")
        ui.code(state.model.model_dump_json(indent=2), language="json")

    return state


@ui.page("/")
def index() -> None:
    create_app()


ui.run_with(fastapi_app, title="PID Controller Web UI")


def main() -> None:
    """Start the NiceGUI application."""
    import uvicorn

    uvicorn.run("webui.app:fastapi_app", reload=True)


if __name__ == "__main__":
    main()
