import logging
from typing import List, Tuple
import asyncio
import cv2
import numpy as np
from pydantic import BaseModel
from fastapi import WebSocket, WebSocketDisconnect

from conf.config import settings

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


class CascadeClassierFun:

    cascade_classifier: cv2.CascadeClassifier

    def __init__(self):
        self.cascade_classifier = cv2.CascadeClassifier()

    def detect(self, gray):
        return self.cascade_classifier.detectMultiScale(gray)

    def load(self):
        self.cascade_classifier.load(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore
        )
        return self.detect
