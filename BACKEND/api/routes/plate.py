import logging
from fastapi import APIRouter, UploadFile, HTTPException
from conf.config import settings
from services.services import plate_recognize_tf

router = APIRouter(prefix="/plate", tags=["plate"])

logger = logging.getLogger(f"{settings.app_name}.{__name__}")


@router.post("/detection", description="Input image is UploadFile")
async def plate_recognize(file: UploadFile):
    try:
        # print(f"plate_recognize : {file}")
        image = await file.read()  # Read the file content as bytes
        result = await plate_recognize_tf(image)
        # print(f"{result=}")
        return result
    except Exception as e:
        print({str(e)})
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
