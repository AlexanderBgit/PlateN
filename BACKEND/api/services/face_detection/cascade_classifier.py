import logging
from typing import List, Tuple

import cv2

from conf.config import settings
from services.face_detection.image_queue import (
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

    queue: int | None = None


class CascadeClassierFun(AbstractFun):
    cascade_classifier: cv2.CascadeClassifier

    def __init__(self):
        self.cascade_classifier = cv2.CascadeClassifier()

    def detect(self, img, queue_id: int = None) -> dict:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        detected_faces = self.cascade_classifier.detectMultiScale(gray)
        if len(detected_faces) > 0:
            objects: List[DetectedObject] = [
                DetectedObject(boundary=obj) for obj in detected_faces.tolist()
            ]
            objects_output = Faces(objects=objects, queue=queue_id)  # type: ignore
        else:
            objects_output = Faces(objects=[])
        return objects_output.dict()

    def get(self):
        return self.detect

    def load(self):
        self.cascade_classifier.load(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore
        )
