import logging
import cv2

from conf.config import settings
from services.face_detection.image_queue import AbstractFun

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


class CascadeClassierFun(AbstractFun):
    cascade_classifier: cv2.CascadeClassifier

    def __init__(self):
        self.cascade_classifier = cv2.CascadeClassifier()

    def detect(self, gray):
        return self.cascade_classifier.detectMultiScale(gray)

    def get(self):
        return self.detect

    def load(self):
        self.cascade_classifier.load(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore
        )
