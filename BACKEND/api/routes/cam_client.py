import logging
from enum import Enum

from fastapi import HTTPException, APIRouter, Query
from starlette.requests import Request
from conf.config import settings, templates
from services.utils import relative_url, relative_url_filter


router = APIRouter(prefix="/cam_client", tags=["cam_client"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


class ClientModules(str, Enum):
    face_cc = "face_cc"
    face_yn = "face_yn"


# url = router.url_path_for(route_name, item_id=item_id)


CLIENT_MODULES = {
    ClientModules.face_cc.value: {
        "text_header": "Real time face detection (OpenCV Cascade Classifier)",
        "ws_url": "cam_modules",  # route name
        "js_module": "cam_face_casc.js",
    },
    ClientModules.face_yn.value: {
        "text_header": "Real time face detection (OpenCV FaceDetectorYN. Model 'yunet_2023mar') (in development now it is just a plug)",
        "ws_url": "cam_modules",  # route name
        "js_module": "cam_face_casc.js",
    },
}


def get_modules() -> list[dict]:
    return [
        {e.value: CLIENT_MODULES.get(e.value, {}).get("text_header")}
        for e in ClientModules
    ]


@router.get("/modules", name="cam_client_modules")
async def cam_clients_modules(request: Request):
    return get_modules()


@router.get("/list", name="cam_client_list")
async def cam_clients(request: Request):
    context = {
        "request": request,
        "title": "Cam Client lists",
        "text_header": "List of available modules",
        "static_url": settings.static_url,
        "modules": get_modules(),
        "version": settings.version,
    }
    return templates.TemplateResponse("cam_client/index_modules.html", context=context)


@router.get("")
@router.get("/{module}", name="cam_client_module")
async def cam_client(request: Request, module: ClientModules = ClientModules.face_cc):
    client_module = CLIENT_MODULES.get(module)
    if not client_module:
        return HTTPException(status_code=403, detail=f"Module: '{module}' is undefined")
    ws_url = relative_url_filter(request.url_for(client_module.get("ws_url")))
    context = {
        "request": request,
        "title": "Cam Client",
        "text_header": client_module.get("text_header"),
        "ws_url": ws_url,
        "static_url": settings.static_url,
        "version": settings.version,
        "js_module": client_module.get("js_module"),
    }
    return templates.TemplateResponse("cam_client/index.html", context=context)
