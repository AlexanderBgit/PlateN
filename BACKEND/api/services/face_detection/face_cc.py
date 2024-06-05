import logging
from typing import List

import cv2

from conf.config import settings
from services.image_queue import (
    AbstractFun,
    ABSDetected,
    ABSDetectedObject,
)

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


class DetectedObject(ABSDetectedObject): ...


class Faces(ABSDetected):
    """This is a pydantic model to define the structure of the streaming data
    that we will be sending the the cv2 Classifier to make predictions
    It expects a List of a Tuple of 4 integers
    """


class CascadeClassierFun(AbstractFun):
    cascade_classifier: cv2.CascadeClassifier
    max_size = (640 // 2, 480 // 2)
    img_scale = (1.0, 1.0)

    def __init__(self):
        self.cascade_classifier = cv2.CascadeClassifier()

    def check_image_size(self, img: cv2.Mat):
        h, w = img.shape[:2]
        # logger.debug(f"{w=}, {h=}")
        if w > self.max_size[0] or h > self.max_size[1]:
            self.img_scale = (w / self.max_size[0], h / self.max_size[1])
            return cv2.resize(img, self.max_size)
        return img

    def correction_boundary(self, boundary):
        if self.img_scale == (1.0, 1.0):
            return boundary
        x1, y1, x2, y2 = boundary
        x1 = x1 * self.img_scale[0]
        y1 = y1 * self.img_scale[1]
        x2 = x2 * self.img_scale[0]
        y2 = y2 * self.img_scale[1]
        return x1, y1, x2, y2

    def detect(self, img, queue_id: int = None) -> dict:
        gray = cv2.cvtColor(self.check_image_size(img), cv2.COLOR_RGB2GRAY)
        detected_faces = self.cascade_classifier.detectMultiScale(gray)
        # Decode result
        if len(detected_faces) > 0:
            objects: List[DetectedObject] = [
                DetectedObject(boundary=self.correction_boundary(obj)) for obj in detected_faces.tolist()  # type: ignore
            ]
            objects_output = Faces(objects=objects, queue_id=queue_id)
        else:
            objects_output = Faces(objects=[], queue_id=queue_id)
        return objects_output.dict()

    def get(self):
        return self.detect

    def load(self):
        self.cascade_classifier.load(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore
        )
