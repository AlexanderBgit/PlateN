import logging
from typing import Any

from fastapi import FastAPI, Path, Query, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from fastapi.responses import RedirectResponse

from conf.config import settings

logger = logging.getLogger(f"{settings.app_name}")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

from routes import main, plate, face_detection


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

app.mount("/api/v1/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
STATIC_URL = "/api/v1/static/"

app.include_router(main.router, prefix="/api/v1")
app.include_router(plate.router, prefix="/api/v1")
app.include_router(face_detection.router, prefix="/api/v1")


def https_url_for(request: Request, name: str, **path_params) -> str:
    http_url = request.url_for(name, **path_params)
    # Replace 'http' with 'https'
    return str(http_url.replace("http", "https", 1))


@pass_context
def urlx_for(
    context: dict,
    name: str,
    **path_params: Any,
) -> str:
    request: Request = context["request"]
    http_url = request.url_for(name, **path_params)
    if scheme := request.headers.get("X-Forwarded-Proto"):
        print(f"{request.headers=}")
        print(f"{request.base_url=}")
        print(f"{scheme=}")
        return str(http_url.replace(scheme=scheme))
    print(f"{request.base_url=}")
    # http_url = http_url.replace(scheme=scheme)
    return str(http_url)


templates.env.globals["https_url_for"] = https_url_for
templates.env.globals["url_for"] = urlx_for


@app.get("/")
def read_root():
    return {
        "message": f"Welcome to the {settings.app_name} application! on port={settings.app_port_api}"
    }


@app.get("/api/v1/cam_client")
async def cam_client(request: Request):
    ws_url = "/api/v1/face_detection"
    context = {
        "request": request,
        "title": "Cam Client",
        "ws_url": ws_url,
        "static_url": STATIC_URL,
    }
    return templates.TemplateResponse("cam_client/index.html", context=context)


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
