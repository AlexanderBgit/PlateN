import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from starlette.responses import JSONResponse


from conf.config import settings
from services.face_detection.cascade_classifier import CascadeClassierFun
from services.face_detection.image_queue import ImageQueue, AbstractFun
from services.services import model_load_status

router = APIRouter(prefix="/cam_modules", tags=["cam_modules"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")

face_cc_image_queue: None | ImageQueue = None
face_yn_image_queue: None | ImageQueue = None


@router.websocket("face_cc", name="face_cc")
async def face_cc(websocket: WebSocket):
    """
    This is the endpoint that we will be sending request to from the
    frontend
    """

    if face_cc_image_queue is None:
        raise HTTPException(
            status_code=500,
            detail=f"Error not ready face_cc_image_queue.",
        )

    try:
        await face_cc_image_queue.loop(websocket)
    except Exception as e:
        # logger.error(e)
        ...


@router.websocket("face_yn", name="face_yn")
async def face_yn(websocket: WebSocket):
    """
    This is the endpoint that we will be sending request to from the
    frontend
    """

    if face_cc_image_queue is None:
        raise HTTPException(
            status_code=500,
            detail=f"Error not ready face_cc_image_queue.",
        )

    try:
        await face_cc_image_queue.loop(websocket)
    except Exception as e:
        # logger.error(e)
        ...


@router.on_event("startup")
async def startup():
    global face_cc_image_queue
    """
    This tells fastapi to load the classifier upon app startup
    so that we don't have to wait for the classifier to be loaded after making a request
    """
    cc_func = CascadeClassierFun()
    cc_func.load()
    face_cc_image_queue = ImageQueue(cc_func)
    face_yn_image_queue = ImageQueue(cc_func)
