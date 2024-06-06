import logging

from fastapi import HTTPException, APIRouter
from starlette.requests import Request
from conf.config import settings, templates
from routes.cam_modules import ClientModules, CLIENT_MODULES
from services.utils import relative_url_filter


router = APIRouter(prefix="/cam_client", tags=["cam_client"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


# url = router.url_path_for(route_name, item_id=item_id)


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
    client_module = CLIENT_MODULES.get(module.value)
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
