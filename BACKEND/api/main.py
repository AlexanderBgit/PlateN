from fastapi import FastAPI, UploadFile, HTTPException, File
from typing import Annotated
from pathlib import Path
from dotenv import load_dotenv
import os

from services import plate_recognize_tf

BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR.parent.joinpath("deploy").joinpath(".env")
if env_file.exists():
    load_dotenv(env_file)

APP_PORT_API = os.getenv("APP_PORT_API", 9000)

# CORE ...

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": f"Welcome to the application! {APP_PORT_API=}"}


@app.get("/health/")
def health_check():
    return {"status": "ok"}


@app.post("/plate_recognize/")
async def plate_recognize(file: UploadFile):
    try:
        print(f"plate_recognize : {file}")
        image = await file.read()  # Read the file content as bytes
        result = plate_recognize_tf(image)
        # print(f"{result=}")
        return result
    except Exception as e:
        print({str(e)})
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


# initialization service
if __name__ == "__main__":
    import uvicorn

    print("Run dev mode...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=APP_PORT_API)
    except KeyboardInterrupt:
        print("Pressed Ctrl-C, exiting...")
else:
    print(f"Run app as module...")
