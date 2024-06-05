import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from jinja2 import pass_context

from conf.config import settings, templates
from services.utils import relative_url, relative_url_filter

logger = logging.getLogger(f"{settings.app_name}")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

from routes import main, plate, cam_modules, cam_client

# CORE ...

app = FastAPI(docs_url="/docs", root_path=settings.root_path)

origins = [f"http://{settings.app_host_api}:{settings.app_port_api}"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(settings.static_url, StaticFiles(directory="static"), name="static")


app.include_router(main.router, prefix=f"/{settings.api_version}")
app.include_router(plate.router, prefix=f"/{settings.api_version}")
app.include_router(cam_modules.router, prefix=f"/{settings.api_version}")
app.include_router(cam_client.router, prefix=f"/{settings.api_version}")


@pass_context
def url_x_for(
    context: dict,
    name: str,
    **path_params: Any,
) -> str:
    request: Request = context["request"]
    http_url = request.url_for(name, **path_params)
    if scheme := request.headers.get("x-forwarded-proto"):
        http_url = http_url.replace(scheme=scheme)
    if forwarded_port := request.headers.get("x-forwarded-port"):
        http_url = http_url.replace(port=int(forwarded_port))
    return str(http_url)


templates.env.globals["relative_url"] = relative_url
templates.env.filters["relative_url_filter"] = relative_url_filter
templates.env.globals["url_for"] = url_x_for


@app.get("/")
def read_root():
    return {
        "message": f"Welcome to the {settings.app_name} application! on port={settings.app_port_api}"
    }


# initialization service
if __name__ == "__main__":
    import uvicorn

    print("Run dev mode...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=settings.app_port_api)
    except KeyboardInterrupt:
        print("Pressed Ctrl-C, exiting...")
else:
    print(f"Run app as module...")
