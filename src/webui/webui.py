from __future__ import annotations

import contextlib
import logging
import typing

import uvicorn
from fastapi import FastAPI, HTTPException
from nicegui import ui

from datamodel.pid_controller import ModelSystemDual
from utils import util_datasources, util_logging, util_observer, util_pydantic
from webui.widgets import simple_editors

logger = logging.getLogger(__file__)

util_logging.init_logging()

class WebUIState:
    def __init__(self) -> None:
        self.observer = util_observer.Observer()
        self.model = ModelSystemDual()
        self.hierarchy = util_pydantic.ModelHierarchy.factory(model=self.model)
        self.uart_connected = False
        for element in self.hierarchy.all_elements:
            self.observer.register_with_value(path=element.path, value=element.value)

        self.hierarchy_text = "..."

        def observer_callback(path: str, value: typing.Any) -> None:
            # def x(value: typing.Any) -> str:
            #     if isinstance(value, int):
            #         return f"int({value})"
            #     if isinstance(value, float):
            #         return f"float({value})"
            #     return f"'{value}'"

            self.hierarchy_text = "\n".join(
                [f"{f.path} {repr(f.value)}" for f in webui_state.hierarchy.all_elements]
            )

        self.observer.register_observer_callback(callback=observer_callback)


webui_state = WebUIState()


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI):
    await util_datasources.namedpipe_task(observer=webui_state.observer)
    try:
        yield
    finally:
        logger.info("Done")


app = FastAPI(lifespan=lifespan)


@app.api_route("/customer_api/set_request", methods=["GET"])
async def customer_api_set_request(path: str, value: str) -> dict[str, typing.Any]:
    item = webui_state.observer.get_item(path=path)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Unknown path: {path}")

    try:
        _value = eval(value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    value_new = await webui_state.observer.set_request(path=path, value=_value)
    return {
        "ok": True,
        "path": path,
        "value": value_new,
    }


async def create_app() -> None:
    """PID Controller Web UI"""

    # with ui.column().classes("w-full max-w-2xl gap-0 p-4"):
    def dump_elements(mh: util_pydantic.ModelHierarchy) -> None:
        assert isinstance(mh, util_pydantic.ModelHierarchy)
        for path, item in mh.elements.items():
            print(f"element:  {path} - {item.value_type_name}")
            try:
                f_create_field = simple_editors.TYPE_MAP_NICE_GUI[item.value_type]
            except KeyError:
                ui.label(
                    f"{item.field_name}: unsupported field type {item.value_type_name}"
                )
                continue

            with ui.row().classes("w-full items-center gap-0 p-0 pl-4"):
                f_create_field(observer=webui_state.observer, path=path, field=item)

    def dump(mh: util_pydantic.ModelHierarchy) -> None:
        assert isinstance(mh, util_pydantic.ModelHierarchy)

        use_tabs = False
        if use_tabs:
            # Tabs
            dict_tabs = {}

            with ui.tabs().classes("w-full") as tabs:
                for path, item in mh.compounds.items():
                    # dict_tabs[path] = ui.tab(f"{path}: {item.title}")
                    dict_tabs[path] = ui.tab(item.title)

                dict_tabs["/custom"] = ui.tab("customized")

            with ui.tab_panels(tabs).classes("w-full"):
                for path, item in mh.compounds.items():
                    current_tab = dict_tabs[path]
                    with ui.tab_panel(current_tab).classes("w-full"):
                        print(f"compount: {path} - {item.model!r}")
                        dump_elements(mh=item)

                current_tab = dict_tabs["/custom"]
                with ui.tab_panel(current_tab).classes("w-full"):
                    ui.label("Customized")

        else:
            # Expansion
            for path, item in mh.compounds.items():
                with ui.expansion(item.title, value=True).classes("w-full"):
                    print(f"compound: {path} - {item.model!r}")
                    dump_elements(mh=item)

            with ui.expansion("Custom").classes("w-full"):
                with ui.row().classes("w-full items-center gap-0 p-0 pl-4"):
                    path = "/common/debuglevel"
                    simple_editors.create_selection_field(
                        options={
                            0: "off",
                            1: "debug",
                            2: "info",
                            3: "warn",
                            4: "error",
                        },
                        observer=webui_state.observer,
                        path=path,
                        field=mh.get_by_path(path).field,
                    )

                with ui.row().classes("w-full items-center gap-0 p-0 pl-4"):
                    path = "/axis_x/value"
                    simple_editors.create_slider_field(
                        observer=webui_state.observer,
                        path=path,
                        field=mh.get_by_path(path).field,
                    )

                with ui.row().classes("w-full items-center gap-0 p-0 pl-4"):
                    ui.code().bind_content_from(webui_state, "hierarchy_text")

    if True:
        log = ui.log(max_lines=10).classes("w-full h-20")
        handler = util_logging.LogElementHandler(element=log, level=logging.DEBUG)
        logging.getLogger().addHandler(handler)
    if True:
        ui.checkbox(
            "UART connected",
            on_change=lambda event: webui_state.observer.set_quality_known(event.value),
        ).bind_value(webui_state, "uart_connected")

    dump(mh=webui_state.hierarchy)



@ui.page("/")
async def index() -> None:
    await create_app()


ui.run_with(app, title="PID Controller Web UI")


def main() -> None:
    """Start the WebUI application."""

    uvicorn.run("webui.webui:app", reload=True)


if __name__ == "__main__":
    main()
