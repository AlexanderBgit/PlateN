import configparser
from os import environ
from pathlib import Path
from typing import Optional

from pydantic import AnyHttpUrl, field_validator, validator

# from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from starlette.templating import Jinja2Templates

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
        proj_name = config["tool.poetry"]["name"].strip('"').strip()
        proj_version = config["tool.poetry"]["version"].strip('"').strip()
        ver_list = [proj_version]
        if git_version:
            ver_list.append(git_version)
        ver = "-".join(ver_list)
        context = {"name": proj_name, "version": ver}
    return context


templates: Jinja2Templates = Jinja2Templates(directory="templates")


class Settings(BaseSettings):
    app_name: str = "fastparking-api"
    app_host_api: str = "0.0.0.0"
    app_port_api: int = 9000
    api_port_websocket: int = 9090
    api_use_plate_ds: bool = True
    version: dict = get_version()
    root_path: str = "/api"
    api_version: str = "v1"

    @property
    def static_url(self) -> str:
        url_list = []
        if hasattr(self, "root_path") and self.root_path:
            url_list.append(self.root_path)
        else:
            url_list.append("")
        if hasattr(self, "api_version") and self.api_version:
            url_list.append(self.api_version)
        url_list.append("static/")
        result = "/".join(url_list)
        # print(result)
        return result

    class Config:
        extra = "ignore"
        env_file = BASE_PATH.joinpath("deploy", ".env")
        env_file_encoding = "utf-8"


settings = Settings()


if __name__ == "__main__":
    print(settings.Config.env_file)
    print(settings)
