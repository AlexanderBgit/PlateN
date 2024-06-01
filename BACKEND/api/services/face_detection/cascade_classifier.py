import logging
from typing import List, Tuple
import asyncio
import cv2
import numpy as np
from pydantic import BaseModel
from fastapi import WebSocket, WebSocketDisconnect

from conf.config import settings

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


# initialize the classifier that we will use
cascade_classifier = cv2.CascadeClassifier()


class Faces(BaseModel):
    """This is a pydantic model to define the structure of the streaming data
    that we will be sending the the cv2 Classifier to make predictions
    It expects a List of a Tuple of 4 integers
    """

    faces: List[Tuple[int, int, int, int]]


async def receive(websocket: WebSocket, queue: asyncio.Queue):
    """
    This is the asynchronous function that will be used to receive webscoket
    connections from the web page
    """
    bytes = await websocket.receive_bytes()
    try:
        queue.put_nowait(bytes)
    except asyncio.QueueFull:
        pass


async def detect(websocket: WebSocket, queue: asyncio.Queue):
    """
    This function takes the received request and sends it to our classifier
    which then goes through the data to detect the presence of a human face
    and returns the location of the face from the continous stream of visual data as a
    list of Tuple of 4 integers that will represent the 4 Sides of a rectangle
    """
    while True:
        bytes = await queue.get()
        data = np.frombuffer(bytes, dtype=np.uint8)
        img = cv2.imdecode(data, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        faces = cascade_classifier.detectMultiScale(gray)
        if len(faces) > 0:
            faces_output = Faces(faces=faces.tolist())  # type: ignore
        else:
            faces_output = Faces(faces=[])
        await websocket.send_json(faces_output.dict())


async def face_detection_srv(websocket: WebSocket):
    """
    This is the endpoint that we will be sending request to from the
    frontend
    """
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue(maxsize=10)
    detect_task = asyncio.create_task(detect(websocket, queue))
    try:
        while True:
            await receive(websocket, queue)
    except WebSocketDisconnect:
        detect_task.cancel()
        await websocket.close()


async def startup_srv():
    """
    This tells fastapi to load the classifier upon app startup
    so that we don't have to wait for the classifier to be loaded after making a request
    """
    cl = cascade_classifier.load(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore
    )
