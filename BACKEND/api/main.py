from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR.parent.joinpath("deploy").joinpath(".env")
if env_file.exists():
    load_dotenv(env_file)

APP_PORT_API = os.getenv("API_APP_PORT", 9000)

# CORE ...

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": f"Welcome to the application! {APP_PORT_API=}"}


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
