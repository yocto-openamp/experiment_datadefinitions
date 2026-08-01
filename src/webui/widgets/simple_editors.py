from __future__ import annotations

import typing

import annotated_types
import nicegui
import nicegui.element
import nicegui.events
import pydantic_core
from nicegui import ui

from utils import util_observer
from utils.util_pydantic import FieldInfoIter

STYLE_QUALITY = "pl-4 text-blue"
PROPS_ENTRY = "borderless dense"
STYLE_ENTRY = "p-0"  # "flex-1 min-h-0 p-0"
STYLE_COMMENT = "pl-4 text-green"

async def set_and_validate(
    observer: util_observer.Observer,
    path: str,
    field: FieldInfoIter,
    event: nicegui.events.UiEventArguments,
) -> None:
    assert isinstance(path, str)
    assert isinstance(field, FieldInfoIter)
    assert isinstance(event, nicegui.events.UiEventArguments)
    if isinstance(event, nicegui.events.ValueChangeEventArguments):
        value = event.value
        try:
            field.set_value(value)
        except pydantic_core.ValidationError as e:
            msg = e.errors()[0]["msg"]
            event.sender.error = msg

        await observer.set_request(path=path, value=value)

    pass


def _attach_comment_tooltip(
    widget: nicegui.element.Element,
    field: FieldInfoIter,
) -> None:
    if field.schema_extra.comment:
        ui.label(field.schema_extra.comment).classes(STYLE_COMMENT)


def create_text_field(
    observer: util_observer.Observer,
    path: str,
    field: FieldInfoIter,
) -> None:
    observable = observer.get_item(path=path)
    unit = field.schema_extra.unit

    ui.label(field.title).classes("min-w-24 font-medium leading-none p-0")
    value = field.get_value()

    widget = (
        ui.input(
            value=value,
            suffix=unit,
            on_change=lambda event: set_and_validate(
                observer=observer,
                path=path,
                field=field,
                event=event,
            ),
        )
        .props(PROPS_ENTRY)
        .classes(STYLE_ENTRY)
        .bind_value(observable, "value")
    )
    ui.label(text="...").classes(STYLE_QUALITY).bind_text_from(
        observable, "quality_text"
    )
    if field.schema_extra.comment:
        ui.label(field.schema_extra.comment).classes(STYLE_COMMENT)


def create_integer_field(
    observer: util_observer.Observer,
    path: str,
    field: FieldInfoIter,
) -> None:
    observable = observer.get_item(path=path)
    unit = field.schema_extra.unit

    ui.label(field.title).classes("min-w-24 font-medium leading-none p-0")
    value = field.get_value()
    widget = (
        ui.number(
            value=value,
            min=field.get_annotation(annotated_types.Ge).ge,
            max=field.get_annotation(annotated_types.Le).le,
            step=1,
            suffix=unit,
            on_change=lambda event: set_and_validate(
                observer=observer,
                path=path,
                field=field,
                event=event,
            ),
        )
        .props(PROPS_ENTRY)
        .classes(STYLE_ENTRY)
        .bind_value(observable, "value")
    )
    ui.label(text="...").classes(STYLE_QUALITY).bind_text_from(
        observable, "quality_text"
    )
    if field.schema_extra.comment:
        ui.label(field.schema_extra.comment).classes(STYLE_COMMENT)


def create_slider_field(
    observer: util_observer.Observer,
    path: str,
    field: FieldInfoIter,
) -> None:
    observable = observer.get_item(path=path)

    ui.label(field.title).classes("min-w-24 font-medium leading-none p-0")
    value = field.get_value()
    widget = (
        ui.slider(
            value=value,
            min=field.get_annotation(annotated_types.Ge).ge,
            max=field.get_annotation(annotated_types.Le).le,
            step=1,
            on_change=lambda event: set_and_validate(
                observer=observer,
                path=path,
                field=field,
                event=event,
            ),
        )
        .props(PROPS_ENTRY)
        .classes(STYLE_ENTRY)
        .bind_value(observable, "value")
    )
    ui.label(text="...").classes(STYLE_QUALITY).bind_text_from(
        observable, "quality_text"
    )
    if field.schema_extra.comment:
        ui.label(field.schema_extra.comment).classes(STYLE_COMMENT)


def create_selection_field(
    observer: util_observer.Observer,
    path: str,
    field: FieldInfoIter,
    options: list | dict,
) -> None:
    observable = observer.get_item(path=path)

    ui.label(field.title).classes("min-w-24 font-medium leading-none p-0")
    value = field.get_value()
    widget = (
        ui.select(
            options=options,
            value=value,
            on_change=lambda event: set_and_validate(
                observer=observer,
                path=path,
                field=field,
                event=event,
            ),
        )
        .props(PROPS_ENTRY)
        .classes(STYLE_ENTRY)
        .bind_value(observable, "value")
    )
    ui.label(text="...").classes(STYLE_QUALITY).bind_text_from(
        observable, "quality_text"
    )
    if field.schema_extra.comment:
        ui.label(field.schema_extra.comment).classes(STYLE_COMMENT)


def create_float_field(
    observer: util_observer.Observer,
    path: str,
    field: FieldInfoIter,
) -> None:
    observable = observer.get_item(path=path)
    unit = field.schema_extra.unit

    ui.label(field.title).classes("min-w-24 font-medium leading-none p-0")
    value = field.get_value()

    widget = (
        ui.number(
            value=value,
            min=field.schema.get("minimum"),
            max=field.schema.get("maximum"),
            step=0.1,
            suffix=unit,
            on_change=lambda event: set_and_validate(
                observer=observer,
                path=path,
                field=field,
                event=event,
            ),
        )
        .props(PROPS_ENTRY)
        .classes(STYLE_ENTRY)
        .bind_value(observable, "value")
    )
    ui.label(text="...").classes(STYLE_QUALITY).bind_text_from(
        observable, "quality_text"
    )
    if field.schema_extra.comment:
        ui.label(field.schema_extra.comment).classes(STYLE_COMMENT)


class TypeMapNiceGUI(
    dict[
        type,
        typing.Callable[
            [util_observer.Observer, str, FieldInfoIter],
            None,
        ],
    ]
):
    pass


TYPE_MAP_NICE_GUI = TypeMapNiceGUI(
    {
        str: create_text_field,
        int: create_integer_field,
        float: create_float_field,
    }
)
