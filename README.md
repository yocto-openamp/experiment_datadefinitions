# experiment_datadefinitions

Using pydantic to specify the datamodel

## Core objectives

Development efforts should be focused on the company's core competencies. Software modules that serve only as infrastructure should, wherever possible, be generic or automatically generated.

This is enabled by a technology stack that minimizes the number of different programming languages and concepts used.

## Technology stack

Developer priority

* Relevant: 🎯 Must learn and understand the core concept
* Nice to know: 💡
* Under the hood: ⚙️ You hardly will get in touch with this


Stack

* Languages
  * 🎯 C on M7
  * 🎯 Python on Linux
* Linux
  * Distribution ⚙️ [yocto](https://www.yoctoproject.org/), ⚙️ [Torizon](https://www.torizon.io/)
* Python stack
  * 🎯 [asyncio](https://docs.python.org/3/library/asyncio.html)
  * datamodel: 🎯 [pydantic](https://pydantic.dev/) at the full glory
  * tests: 💡 [pytest](https://pytest.org/)
 * Templating Engine: 💡 [Jinja2](https://jinja.palletsprojects.com/en/stable/)
* AMP stack
  * OpenAMP: 💡 [remoteproc](https://openamp.readthedocs.io/en/latest/protocol_details/lifecyclemgmt.html) und 💡 [rpmsg](https://openamp.readthedocs.io/en/latest/protocol_details/rpmsg.html)
  * C to Python communication: Python ⚙️ [ctypes](https://docs.python.org/3/library/ctypes.html#ctypes-fundamental-data-types-2)
* Web stack
  * Web: 💡 [FastAPI](https://fastapi.tiangolo.com/)
    * Asynchronous Server Gateway Interface: ⚙️ [starlette](https://starlette.dev/)
    * Web Server: ⚙️ [uvicorn](https://uvicorn.dev/)
  * Web UI: 🎯 [NiceGUI](https://nicegui.io/)
    * UI Styling: ⚙️ [Tailwind CSS](https://tailwindcss.com/)
    * UI Elements ⚙️ [VueJs/Quasar](https://quasar.dev/)
    * Icons: ⚙️ [Google Material Icons](https://fonts.google.com/icons)
* Infrastrucure
  * IDE: 🎯 [Visual Studio Code](https://code.visualstudio.com/)
  * Virtualization: 💡 [Docker](https://www.docker.com/), ⚙️ [Devcontainer](https://containers.dev/), 💡 [Github Codespaces](https://github.com/features/codespaces). This is used for building and regression testing

## Setting values via named pipe

```bash
echo "/axis_x/value int(56)" > namedpipe
```