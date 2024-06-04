import logging
from enum import Enum

from fastapi import HTTPException, APIRouter
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from conf.config import settings, templates

router = APIRouter(prefix="/cam_client", tags=["cam_client"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


class ClientModules(str, Enum):
    face_cc = "face_cc"
    face_yn = "face_yn"


CLIENT_MODULES = {
    ClientModules.face_cc.value: {
        "text_header": "Real time face detection (OpenCV Cascade Classifier)",
        "ws_url": "/api/v1/face_detection",
        "js_module": "cam_face_casc.js",
    },
    ClientModules.face_yn.value: {
        "text_header": "Real time face detection (OpenCV FaceDetectorYN. Model 'yunet_2023mar')",
        "ws_url": "/api/v1/face_detection",
        "js_module": "cam_face_casc.js",
    },
}


@router.get("")
async def cam_clients(request: Request):
    context = {
        "request": request,
        "title": "Cam Client lists",
        "text_header": "List of available clients",
        "static_url": settings.static_url,
        "modules": CLIENT_MODULES,
        "version": settings.version,
    }
    return templates.TemplateResponse("cam_client/index_modules.html", context=context)


@router.get("/modules")
async def cam_clients_modules(request: Request):
    return [e.value for e in ClientModules]


@router.get("/{module}")
async def cam_client(request: Request, module: ClientModules = ClientModules.face_cc):
    client_module = CLIENT_MODULES.get(module)
    if not client_module:
        return HTTPException(status_code=404, detail=f"Module: '{module}' is undefined")
    context = {
        "request": request,
        "title": "Cam Client",
        "text_header": client_module.get("text_header"),
        "ws_url": client_module.get("ws_url"),
        "static_url": settings.static_url,
        "version": settings.version,
        "js_module": client_module.get("js_module"),
    }
    return templates.TemplateResponse("cam_client/index.html", context=context)
