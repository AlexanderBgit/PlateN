import logging
import time
from pathlib import Path
from types import NoneType
from typing import List, Tuple

import cv2

from conf.config import settings
from services.image_queue import (
    AbstractFun,
    ABSDetected,
    ABSDetectedObject,
)

logger = logging.getLogger(f"{settings.app_name}.{__name__}")
logger.setLevel(logging.DEBUG)


class QrWeChat:
    def __init__(
        self,
        model_path: Path,
        input_size=(320, 320),
    ):
        # INITIALIZATION.
        # Instantiate QR Code detector object.
        detector_prototxt_path = model_path.joinpath("detect.prototxt")
        detector_caffe_model_path = model_path.joinpath("detect.caffemodel")
        super_resolution_prototxt_path = model_path.joinpath("sr.prototxt")
        super_resolution_caffe_model_path = model_path.joinpath("sr.caffemodel")
        try:
            if not detector_prototxt_path.exists():
                raise AssertionError(f"models path not found {detector_prototxt_path}")
            self.detector = cv2.wechat_qrcode.WeChatQRCode(
                detector_prototxt_path=str(detector_prototxt_path),
                detector_caffe_model_path=str(detector_caffe_model_path),
                super_resolution_prototxt_path=str(super_resolution_prototxt_path),
                super_resolution_caffe_model_path=str(
                    super_resolution_caffe_model_path
                ),
            )
        except Exception as err:
            logger.error(err)

    def scale_image(self, image, max_size=640):
        h, w = image.shape[:2]
        if max(h, w) > max_size:
            scale_factor = max_size / max(h, w)
            image = cv2.resize(
                image,
                (int(w * scale_factor), int(h * scale_factor)),
                interpolation=cv2.INTER_AREA,
            )
        return image

    def run(self, frame):
        # Detect and decode.
        res, points = self.detector.detectAndDecode(frame)
        return points, res


class DetectedObject(ABSDetectedObject):
    boundary: List[Tuple[int, int]]
    text: str


class QrData(ABSDetected):
    """This is a pydantic model to define the structure of the streaming data
    that we will be sending the the cv2 Classifier to make predictions
    It expects a List of a Tuple of 8 integers
    """

    objects: List[DetectedObject]


class QrWeChatFun(AbstractFun):
    qr_wechat: QrWeChat
    max_size = (512, 512)  # for DNN model size
    img_scale = (1.0, 1.0)

    def __init__(self):
        BASE_PATH = Path(__file__).resolve().parent
        model_path = BASE_PATH.joinpath("models", "wechat_cv")
        input_size = self.max_size
        self.qr_wechat = QrWeChat(
            model_path=model_path,
        )

    def check_image_size(self, img: cv2.Mat):
        h, w = img.shape[:2]
        # logger.debug(f"{w=}, {h=}")
        if w > self.max_size[0] or h > self.max_size[1]:
            self.img_scale = (w / self.max_size[0], h / self.max_size[1])
            return cv2.resize(
                img,
                self.max_size,
                interpolation=cv2.INTER_AREA,
            )
        return img

    def correction_boundary(self, boundary):
        if self.img_scale == (1.0, 1.0):
            return boundary
        x, y, width, height = boundary
        x = x * self.img_scale[0]
        y = y * self.img_scale[1]
        width = width * self.img_scale[0]
        height = height * self.img_scale[1]
        return x, y, width, height

    def detect(self, img, queue_id: int = None) -> dict:
        """
        img is BGR
        """
        try:
            img = cv2.cvtColor(self.check_image_size(img), cv2.COLOR_BGR2GRAY)
            img = self.check_image_size(img)
            detected_faces, detected_texts = self.qr_wechat.run(img)
            # Decode result
            if detected_faces is not None and len(detected_faces) > 0:
                # logger.debug(f"{detected_faces=}")
                objects: List[DetectedObject] = []
                for i, face in enumerate(detected_faces):
                    boundary_lines = face.astype(int)
                    # x, y = boundary_lines[0]
                    # width = boundary_lines[2][0] - x
                    # height = boundary_lines[2][1] - y
                    # # boundary = (x, y, width, height)
                    detected_object = DetectedObject(
                        boundary=boundary_lines, text=detected_texts[i]
                    )
                    objects.append(detected_object)
                    # logger.debug(f"{detected_object=}")

                objects_output = QrData(objects=objects, queue_id=queue_id)
            else:
                objects_output = QrData(objects=[], queue_id=queue_id)
        except Exception as err:
            objects_output = QrData(objects=[], queue_id=queue_id, error=str(err))
        return objects_output.dict()

    def get(self):
        return self.detect

    def load(self): ...
