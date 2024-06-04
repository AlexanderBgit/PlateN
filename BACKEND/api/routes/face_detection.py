import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from starlette.responses import JSONResponse


from conf.config import settings
from services.face_detection.cascade_classifier import CascadeClassierFun
from services.face_detection.image_queue import ImageQueue, AbstractFun
from services.services import model_load_status

router = APIRouter(prefix="/face_detection", tags=["face_detection"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")

face_detection_image_queue: None | ImageQueue = None


@router.websocket("", name="face_detection")
async def face_detection(websocket: WebSocket):
    """
    This is the endpoint that we will be sending request to from the
    frontend
    """

    if face_detection_image_queue is None:
        raise HTTPException(
            status_code=500,
            detail=f"Error not ready face_detection_image_queue.",
        )

    try:
        await face_detection_image_queue.loop(websocket)
    except Exception as e:
        # logger.error(e)
        ...


@router.on_event("startup")
async def startup():
    global face_detection_image_queue
    """
    This tells fastapi to load the classifier upon app startup
    so that we don't have to wait for the classifier to be loaded after making a request
    """
    cc_func = CascadeClassierFun()
    cc_func.load()
    face_detection_image_queue = ImageQueue(cc_func)
