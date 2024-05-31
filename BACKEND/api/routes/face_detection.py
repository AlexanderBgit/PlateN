import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.responses import JSONResponse


from conf.config import settings
from services.face_detection.fd_srv import face_detection_srv, startup_srv
from services.services import model_load_status

router = APIRouter(prefix="/face_detection", tags=["face_detection"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


@router.websocket("/")
async def face_detection(websocket: WebSocket):
    """
    This is the endpoint that we will be sending request to from the
    frontend
    """
    await face_detection_srv(websocket)


@router.on_event("startup")
async def startup():
    """
    This tells fastapi to load the classifier upon app startup
    so that we don't have to wait for the classifier to be loaded after making a request
    """
    await startup_srv()
