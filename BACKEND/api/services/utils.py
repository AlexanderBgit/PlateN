from urllib.parse import urlparse, urlencode, urlunparse, parse_qs

from starlette.requests import Request

from conf.config import get_version


def relative_url(request: Request, name: str, **path_params) -> str:
    absolute_url = str(request.url_for(name, **path_params))
    root_path = request.app.root_path
    return absolute_url.replace(str(request.base_url), root_path + "/")


def relative_url_filter(absolute_url) -> str:
    if not isinstance(absolute_url, str):
        absolute_url = str(absolute_url)
    parsed_url = urlparse(absolute_url)
    return parsed_url.path


def url_add_param(input_url: str, param_name: str, param_value: str) -> str:
    # Query parameters to add
    params = {param_name: param_value}
    # Parse the original URL into components
    url_parts = list(urlparse(input_url))
    if url_parts:
        # Parse existing query parameters and update with new ones
        query = parse_qs(url_parts[4])
        query.update(params)
        # Encode the updated query parameters
        url_parts[4] = urlencode(query, doseq=True)
        # Reconstruct the URL with the new query parameters
        return urlunparse(url_parts)
    return input_url


def url_add_ver(input_url: str) -> str:
    ver = get_version().get("hash")
    if ver:
        return url_add_param(input_url, "v", ver)
    return input_url
