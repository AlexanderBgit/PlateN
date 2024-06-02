import configparser
from os import environ
from pathlib import Path

# from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_BACKEND = Path(__file__).resolve().parent.parent.parent
BASE_PATH = BASE_BACKEND.parent

# load_dotenv(BASE_PATH.joinpath("deploy," ".env"))


def get_version():
    git_version = ""
    proj_name = ""
    print(f"{BASE_BACKEND=}")
    GIT_VERSION_FILE = BASE_BACKEND.joinpath("git-version.txt")
    if GIT_VERSION_FILE.exists():
        git_version = GIT_VERSION_FILE.read_text().strip()

    proj_version = ""
    context = {}
    PYPROJECT_FILE = BASE_BACKEND.joinpath("pyproject.toml")
    if PYPROJECT_FILE.exists():
        config = configparser.ConfigParser()
        try:
            config.read(PYPROJECT_FILE)
        except configparser.Error:
            ...
        proj_name = config["tool.poetry"]["name"].strip('"')
        proj_version = config["tool.poetry"]["version"].strip('"')
        ver = "-".join([proj_version, git_version])
        context = {"name": proj_name, "version": ver}
    return context


class Settings(BaseSettings):
    app_name: str = "fastparking-api"
    app_host_api: str = "0.0.0.0"
    app_port_api: int = 9000
    api_port_websocket: int = 9090
    api_use_plate_ds: bool = True
    version: dict = get_version()

    class Config:
        extra = "ignore"
        env_file = BASE_PATH.joinpath("deploy", ".env")
        env_file_encoding = "utf-8"


settings = Settings()

if __name__ == "__main__":
    print(settings.Config.env_file)
    print(settings)
