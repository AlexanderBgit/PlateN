import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse


from ds.predict_num import model_load_status
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


@app.get("/api/v1/health/")
def health_check():
    if model_load_status is not None:
        return JSONResponse(content={"status": "ok"})
    else:
        return JSONResponse(content={"status": "loading"}, status_code=500)


@app.post("/api/v1/plate_recognize/")
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
