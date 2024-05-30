import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from conf.config import settings

from routes import main, plate


logger = logging.getLogger(f"{settings.app_name}")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# CORE ...

app = FastAPI()

origins = [f"http://{settings.app_host_api}:{settings.app_port_api}"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(main.router, prefix="/api/v1")
app.include_router(plate.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": f"Welcome to the application! {settings.app_port_api=}"}


# initialization service
if __name__ == "__main__":
    import uvicorn

    print("Run dev mode...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=settings.app_port_api)
    except KeyboardInterrupt:
        print("Pressed Ctrl-C, exiting...")
else:
    print(f"Run app as module...")
