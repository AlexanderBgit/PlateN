import logging
import struct
from abc import abstractmethod
import time
from typing import List, Tuple
import asyncio
import aiofiles
import cv2
import numpy as np
from pydantic import BaseModel
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from conf.config import settings, BASE_BACKEND

logger = logging.getLogger(f"{settings.app_name}.{__name__}")
logger.setLevel(logging.DEBUG)


class ABSDetectedObject(BaseModel):
    # x, y, width, height
    boundary: Tuple[int, int, int, int]


class ABSDetected(BaseModel):
    """This is a pydantic model to define the structure of the streaming data
    that we will be sending the the cv2 Classifier to make predictions
    It expects a List of a Tuple of 4 integers
    """

    objects: List[ABSDetectedObject]
    queue_id: int | None = None
    error: str | None = None


class AbstractFun:
    @abstractmethod
    def get(self): ...

    @abstractmethod
    def load(self): ...

    @abstractmethod
    def detect(self, img, queue_id: int = None) -> dict:
        detected = [(0, 0, 200, 100), (50, 10, 200, 100)]
        if len(detected) > 0:
            objects: List[ABSDetectedObject] = [
                ABSDetectedObject(boundary=obj) for obj in detected
            ]
            objects_output = ABSDetected(objects=objects, queue_id=queue_id)
        else:
            objects_output = ABSDetected(objects=[], queue_id=queue_id)
        return objects_output.dict()


class ImageQueue:

    img_proc: AbstractFun | None = None
    command_size: int = 4

    def __init__(self, img_proc):
        self.img_proc = img_proc

    def encode_message(self, message: bytes):
        (command_id,) = struct.unpack(
            "<I", message[: self.command_size]
        )  # Unpack first COMMAND_SIZE bytes
        image_data = message[self.command_size :]
        return (
            command_id,
            image_data,
        )

    def unpack_message(self, data):

        # for i, byte in enumerate(data[:10]):
        #     logger.debug(f"data [{i}]: {hex(byte)}")

        # Read the header length (1 byte)
        header_length = data[0]

        # Extract the header
        header = data[1 : 1 + header_length].decode("utf-8")
        file_type, command_id = header.split(",")

        # Extract the binary payload
        binary_data = data[1 + header_length :]

        # for i, byte in enumerate(binary_data[:5]):
        #     logger.debug(f"binary_data [{i}]: {hex(byte)}")

        return file_type, int(command_id), binary_data

    async def receive(self, websocket: WebSocket, queue: asyncio.Queue):
        """
        This is the asynchronous function that will be used to receive webscoket
        connections from the web page
        """
        bytes = await websocket.receive_bytes()
        try:
            queue.put_nowait(bytes)
        except asyncio.QueueFull as err:
            logger.debug(err)
            ...

    async def save_image(self, image_bytes, counter: int = 0):
        # Define the output file name
        output_filename = BASE_BACKEND.joinpath(
            "api/services/face_detection/outputs", f"output-{counter:06d}.jpg"
        )
        # Asynchronously write the bytes directly to a file
        async with aiofiles.open(output_filename, "wb") as file:
            await file.write(image_bytes)

    async def detect(
        self, websocket: WebSocket, queue: asyncio.Queue, queue_size: int | None = None
    ):
        """
        This function takes the received request and sends it to our classifier
        which then goes through the data to detect the presence of a human face
        and returns the location of the face from the continous stream of visual data as a
        list of Tuple of 4 integers that will represent the 4 Sides of a rectangle
        """
        counter = 0
        while True:
            if not self.img_proc:
                break
            start_time = time.perf_counter_ns()
            try:
                # get bytes from queue
                bytes = await queue.get()
                # logger.debug(f"receive {len(bytes)=}, {queue.qsize()=}")
                # decode command form bytes
                image_type, command_id, image_data = self.unpack_message(bytes)
                # logger.debug(
                #     f"receive {len(bytes)=}  {len(image_data)=}, {command_id=}, {image_type=}"
                # )
                counter += 1
                start_time = time.perf_counter_ns()
                data = np.frombuffer(image_data, dtype=np.uint8)
                # image in BGR format
                img = cv2.imdecode(data, cv2.IMREAD_COLOR)
                # if counter % 10 == 0:
                #     # Save the image as a JPG file
                #     await self.save_image(bytes, counter)
                # detection API
                detected: dict = self.img_proc.get()(img, queue_size)
                # logger.debug(f"{detected=}")
            except Exception as err:
                detected = {"error": f"error: {str(err)}"}
            if detected.get("error"):
                logger.error(f"method detect function: {detected.get('error')}")
            # duration
            duration_ms = (time.perf_counter_ns() - start_time) // 1e6
            detected["duration_ms"] = duration_ms
            if detected.get("error") is None:
                del detected["error"]
            if detected.get("objects") is None or (len(detected["objects"]) == 0):
                del detected["objects"]
            await websocket.send_json(detected)

    async def loop(self, websocket: WebSocket):
        """
        This is the endpoint that we will be sending request to from the
        frontend
        """
        await websocket.accept()
        queue: asyncio.Queue = asyncio.Queue(maxsize=10)
        detect_task = asyncio.create_task(self.detect(websocket, queue, queue.qsize()))
        try:
            while True:
                await self.receive(websocket, queue)
        except WebSocketDisconnect:
            detect_task.cancel()
        finally:
            try:
                if not websocket.client_state == WebSocketState.DISCONNECTED:
                    await websocket.close()
            except Exception as err:
                ...
            detect_task.cancel()
