from urllib.parse import urlparse

from starlette.requests import Request


def relative_url(request: Request, name: str, **path_params) -> str:
    absolute_url = str(request.url_for(name, **path_params))
    root_path = request.app.root_path
    return absolute_url.replace(str(request.base_url), root_path + "/")


def relative_url_filter(absolute_url) -> str:
    if not isinstance(absolute_url, str):
        absolute_url = str(absolute_url)
    parsed_url = urlparse(absolute_url)
    return parsed_url.path
