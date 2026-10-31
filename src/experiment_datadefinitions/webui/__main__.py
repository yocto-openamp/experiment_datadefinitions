from __future__ import annotations

import uvicorn

if __name__ == "__main__":
    uvicorn.run("experiment_datadefinitions.webui.webui:app", reload=True)
