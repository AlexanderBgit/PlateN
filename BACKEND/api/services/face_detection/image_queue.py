import logging
from abc import abstractmethod
from typing import List, Tuple
import asyncio
import cv2
import numpy as np
from pydantic import BaseModel
from fastapi import WebSocket, WebSocketDisconnect

from conf.config import settings

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


class AbstractFun:
    @abstractmethod
    def get(self): ...

    @abstractmethod
    def load(self): ...


class ABSDetectedObject(BaseModel):
    boundary: Tuple[int, int, int, int]


class ABSDetected(BaseModel):
    """This is a pydantic model to define the structure of the streaming data
    that we will be sending the the cv2 Classifier to make predictions
    It expects a List of a Tuple of 4 integers
    """

    objects: List[ABSDetectedObject]


class ImageQueue:

    img_proc: AbstractFun | None = None

    def __init__(self, img_proc):
        self.img_proc = img_proc

    async def receive(self, websocket: WebSocket, queue: asyncio.Queue):
        """
        This is the asynchronous function that will be used to receive webscoket
        connections from the web page
        """
        bytes = await websocket.receive_bytes()
        # logger.debug(f"receive {len(bytes)=}, {queue.qsize()=}")
        try:
            queue.put_nowait(bytes)
        except asyncio.QueueFull as err:
            logger.debug(err)
            ...

    async def detect(self, websocket: WebSocket, queue: asyncio.Queue):
        """
        This function takes the received request and sends it to our classifier
        which then goes through the data to detect the presence of a human face
        and returns the location of the face from the continous stream of visual data as a
        list of Tuple of 4 integers that will represent the 4 Sides of a rectangle
        """
        while True:
            if not self.img_proc:
                break
            bytes = await queue.get()
            data = np.frombuffer(bytes, dtype=np.uint8)
            img = cv2.imdecode(data, 1)
            detected: dict = self.img_proc.get()(img)
            await websocket.send_json(detected)

    async def loop(self, websocket: WebSocket):
        """
        This is the endpoint that we will be sending request to from the
        frontend
        """
        await websocket.accept()
        queue: asyncio.Queue = asyncio.Queue(maxsize=10)
        detect_task = asyncio.create_task(self.detect(websocket, queue))
        try:
            while True:
                await self.receive(websocket, queue)
        except WebSocketDisconnect:
            detect_task.cancel()
            await websocket.close()
