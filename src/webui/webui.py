"""NiceGUI application scaffold for the PID controller model."""

from __future__ import annotations

import dataclasses
import typing

import nicegui
import nicegui.element
import uvicorn
from fastapi import FastAPI
from nicegui import ui

import datamodel.pid_controller as pid_controller_module
from utils.util_pydantic import FieldInfoIter

app = FastAPI()


@dataclasses.dataclass
class WebUIState:
    model: pid_controller_module.ModelPidController = dataclasses.field(
        default_factory=pid_controller_module.ModelPidController
    )


SHARED_STATE = WebUIState()
FIELD_WIDGETS: dict[str, list[typing.Any]] = {}
MODEL_STATE_WIDGETS: list[typing.Any] = []
IS_BROADCASTING = False


def _attach_comment_tooltip(
    widget: nicegui.element.Element,
    field: FieldInfoIter,
) -> None:
    if field.schema_extra.comment:
        widget.tooltip(field.schema_extra.comment)


def _create_text_field(
    state: WebUIState,
    field: FieldInfoIter,
) -> nicegui.element.Element:
    unit = field.schema_extra.unit
    with ui.row().classes("w-full items-center gap-0 p-0"):
        ui.label(field.title).classes("min-w-24 font-medium leading-none p-0")
        widget = (
            ui.input(
                value=getattr(state.model, field.field_name),
                suffix=unit,
                on_change=lambda event: _update_model_field(
                    state, field.field_name, event.value
                ),
            )
            .props("borderless dense")
            .classes("flex-1 min-h-0 p-0")
            .bind_value(state.model, field.field_name)
        )
    _attach_comment_tooltip(widget, field=field)
    return widget


def _create_integer_field(
    state: WebUIState,
    field: FieldInfoIter,
) -> nicegui.element.Element:
    unit = field.schema_extra.unit
    schema = field.field_info.json_schema_extra
    with ui.row().classes("w-full items-center gap-0 p-0"):
        ui.label(field.title).classes("min-w-24 font-medium leading-none p-0")
        widget = (
            ui.number(
                value=getattr(state.model, field.field_name),
                min=schema.get("minimum"),
                max=schema.get("maximum"),
                step=1,
                suffix=unit,
                on_change=lambda event: _update_model_field(
                    state, field.field_name, event.value
                ),
            )
            .props("borderless dense")
            .classes("flex-1 min-h-0 p-0")
            .bind_value(state.model, field.field_name)
        )
    _attach_comment_tooltip(widget, field=field)
    return widget


def _create_float_field(
    state: WebUIState,
    field: FieldInfoIter,
) -> nicegui.element.Element:
    unit = field.schema_extra.unit
    schema = field.field_info.json_schema_extra
    with ui.row().classes("w-full items-center gap-0 p-0"):
        ui.label(field.title).classes("min-w-24 font-medium leading-none p-0")
        widget = (
            ui.number(
                value=getattr(state.model, field.field_name),
                min=schema.get("minimum"),
                max=schema.get("maximum"),
                step=0.1,
                suffix=unit,
                on_change=lambda event: _update_model_field(
                    state, field.field_name, event.value
                ),
            )
            .props("borderless dense")
            .classes("flex-1 min-h-0 p-0")
            .bind_value(state.model, field.field_name)
        )
    _attach_comment_tooltip(widget, field=field)
    return widget


class TypeMapNiceGUI(dict[type, typing.Callable]):
    pass


TYPE_MAP_NICE_GUI = TypeMapNiceGUI(
    {
        str: _create_text_field,
        int: _create_integer_field,
        float: _create_float_field,
    }
)

def _register_widget(field_name: str, widget: nicegui.element.Element) -> None:
    FIELD_WIDGETS.setdefault(field_name, []).append(widget)


def _register_model_state_widget(widget: typing.Any) -> None:
    MODEL_STATE_WIDGETS.append(widget)


def _broadcast_field_update(field_name: str, value: typing.Any) -> None:
    global IS_BROADCASTING
    IS_BROADCASTING = True
    try:
        for widget in FIELD_WIDGETS.get(field_name, []):
            try:
                current_value = getattr(widget, "value", None)
                if current_value != value:
                    widget.set_value(value)
            except RuntimeError:
                # Ignore stale widgets from disconnected clients.
                continue
    finally:
        IS_BROADCASTING = False


def _broadcast_model_state(state: WebUIState) -> None:
    content = state.model.model_dump_json(indent=2)
    for widget in MODEL_STATE_WIDGETS:
        try:
            widget.set_content(content)
        except RuntimeError:
            # Ignore stale widgets from disconnected clients.
            continue


def _update_model_field(state: WebUIState, name: str, value: typing.Any) -> None:
    if IS_BROADCASTING:
        return

    setattr(state.model, name, value)
    new_value = getattr(state.model, name)
    _broadcast_field_update(field_name=name, value=new_value)
    _broadcast_model_state(state=state)
    print(
        f"[webui] model updated: {name}={new_value!r} | model={state.model.model_dump_json()}",
        flush=True,
    )


def create_app(state: WebUIState | None = None) -> WebUIState:
    """Build the NiceGUI screen for the PID controller model."""
    state = state or WebUIState()

    with ui.column().classes("w-full max-w-2xl gap-0 p-4"):
        ui.label("PID Controller").classes("text-2xl font-bold")
        ui.label("Edit the model fields below.").classes("text-sm text-gray-600")

        for field in FieldInfoIter.iter_model(type(state.model)):
            field_type = field.field_info.annotation
            try:
                f_create_field = TYPE_MAP_NICE_GUI[field_type]
            except KeyError:
                ui.label(f"{field.title}: unsupported field type {field_type!r}")
                continue
            widget = f_create_field(state, field)
            _register_widget(field_name=field.field_name, widget=widget)

        ui.separator()
        ui.label("Current model state").classes("text-lg font-semibold")
        model_state_widget = ui.code(
            state.model.model_dump_json(indent=2), language="json"
        )
        _register_model_state_widget(model_state_widget)

    return state


@ui.page("/")
def index() -> None:
    create_app(state=SHARED_STATE)


ui.run_with(app, title="PID Controller Web UI")


def main() -> None:
    """Start the WebUI application."""

    uvicorn.run("webui.webui:app", reload=True)


if __name__ == "__main__":
    main()
