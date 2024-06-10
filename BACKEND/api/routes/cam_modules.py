import logging
from enum import StrEnum

from fastapi import APIRouter, WebSocket, HTTPException

from conf.config import settings
from services.face_detection.face_cc import FaceCascadeClassierFun
from services.face_detection.face_yn import FaceYNFun
from services.image_queue import ImageQueue
from services.qrcode_detection.qr_wechat import QrWeChatFun

router = APIRouter(prefix="/cam_modules", tags=["cam_modules"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


class ClientModules(StrEnum):
    face_cc = "face_cc"
    face_yn = "face_yn"
    qr_wechat = "qr_wechat"


CLIENT_MODULES = {
    ClientModules.face_cc.value: {
        "text_header": "Real time face detection (OpenCV Cascade Classifier)",
        "ws_url": "face_cc",  # route name
        "js_module": "cam_face_cc.js",
    },
    ClientModules.face_yn.value: {
        "text_header": "Real time face detection (OpenCV FaceDetectorYN. Model 'yunet_2023mar')",
        "ws_url": "face_yn",  # route name
        "js_module": "cam_face_yn.js",
    },
    ClientModules.qr_wechat.value: {
        "text_header": "Real time QR code detection (OpenCV WeChatQRCode. Model '2021-3487ef7')",
        "ws_url": "qr_wechat",  # route name
        "js_module": "cam_qr_wechat_lines.js",
        "cam_size": [640, 640],
        "cam_downscale": 1,
        "cam_upscale": 1,
    },
}


image_queues: dict[str, ImageQueue | None] = {
    ClientModules.face_cc: None,
    ClientModules.face_yn: None,
}


@router.websocket("face_cc", name="face_cc")
async def face_cc(websocket: WebSocket):
    """
    This is the endpoint that we will be sending request to from the
    frontend
    """
    face_cc_image_queue = image_queues.get("face_cc")
    if face_cc_image_queue is None:
        raise HTTPException(
            status_code=500,
            detail=f"Error not ready face_cc_image_queue.",
        )

    try:
        await face_cc_image_queue.loop(websocket)
    except Exception as e:
        logger.error(e)
        ...


@router.websocket("face_yn", name="face_yn")
async def face_yn(websocket: WebSocket):
    """
    This is the endpoint that we will be sending request to from the
    frontend
    """
    face_yn_image_queue = image_queues.get("face_yn")
    if face_yn_image_queue is None:
        raise HTTPException(
            status_code=500,
            detail=f"Error not ready face_yn_image_queue.",
        )

    try:
        await face_yn_image_queue.loop(websocket)
    except Exception as e:
        logger.error(e)
        ...


@router.websocket("qr_wechat", name="qr_wechat")
async def qr_wechat(websocket: WebSocket):
    """
    This is the endpoint that we will be sending request to from the
    frontend
    """
    qr_wechat_image_queue = image_queues.get("qr_wechat")
    if qr_wechat_image_queue is None:
        raise HTTPException(
            status_code=500,
            detail=f"Error not ready qr_wechat_image_queue.",
        )

    try:
        await qr_wechat_image_queue.loop(websocket)
    except Exception as e:
        logger.error(e)
        ...


@router.on_event("startup")
async def startup(queues: dict[str, ImageQueue] = None):
    """
    This tells fastapi to load the classifier upon app startup
    so that we don't have to wait for the classifier to be loaded after making a request
    """
    if queues is None:
        queues = image_queues
    cc_func = FaceCascadeClassierFun()
    cc_func.load()
    yn_func = FaceYNFun()
    qr_wechat_func = QrWeChatFun()
    queues["face_cc"] = ImageQueue(cc_func)
    queues["face_yn"] = ImageQueue(yn_func)
    queues["qr_wechat"] = ImageQueue(qr_wechat_func)
