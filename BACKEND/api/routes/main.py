import logging
from fastapi import APIRouter
from starlette.responses import JSONResponse

from conf.config import settings
from services.services import model_load_status

logger = logging.getLogger(f"{settings.app_name}.{__name__}")
router = APIRouter(prefix="", tags=["main"])


@router.get("/health")
def health_check():
    if model_load_status is not None:
        return JSONResponse(content={"status": "ok"})
    else:
        return JSONResponse(content={"status": "loading"}, status_code=500)
