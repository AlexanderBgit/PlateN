from os import environ
from pathlib import Path

# from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_PATH = Path(__file__).resolve().parent.parent.parent.parent
# load_dotenv(BASE_PATH.joinpath("deploy," ".env"))


class Settings(BaseSettings):
    app_name: str = "fastparking-api"
    app_host_api: str = "0.0.0.0"
    app_port_api: int = 9000

    class Config:
        extra = "ignore"
        env_file = BASE_PATH.joinpath("deploy", ".env")
        env_file_encoding = "utf-8"


settings = Settings()

if __name__ == "__main__":
    print(settings.Config.env_file)
    print(settings)
