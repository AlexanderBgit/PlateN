import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from urllib.parse import urlparse


from conf.config import settings, templates

logger = logging.getLogger(f"{settings.app_name}")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

from routes import main, plate, face_detection, cam_client

# CORE ...

app = FastAPI()

origins = [f"http://{settings.app_host_api}:{settings.app_port_api}"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(settings.static_url, StaticFiles(directory="static"), name="static")


app.include_router(main.router, prefix="/api/v1")
app.include_router(plate.router, prefix="/api/v1")
app.include_router(face_detection.router, prefix="/api/v1")
app.include_router(cam_client.router, prefix="/api/v1")


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


def relative_url(request: Request, name: str, **path_params) -> str:
    absolute_url = str(request.url_for(name, **path_params))
    return absolute_url.replace(str(request.base_url), "/")


def relative_url_filter(absolute_url: str) -> str:
    parsed_url = urlparse(absolute_url)
    return parsed_url.path


templates.env.globals["relative_url"] = relative_url

# templates.env.filters["relative_url_filter"] = lambda url, request: relative_url_filter(
#     url, str(request.base_url)
# )
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
