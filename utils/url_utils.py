from urllib.parse import urlparse
from exceptions.InvalidUrlError import InvalidUrlError


# TODO: docs
def grammatically_correct(url: str) -> None:
    try:
        parsed_url = urlparse(url)
    except ValueError:
        raise InvalidUrlError(url)


def is_grammatically_correct(url: str) -> bool:
    try:
        parsed_url = urlparse(url)
        return True
    except ValueError:
        return False


def deduct_second_component(url: str) -> str:
    try:
        parsed_url = urlparse(url)
    except ValueError:
        raise
    scheme = parsed_url.scheme
    result = url.replace(scheme, '')
    if result.startswith('://'):
        if result.endswith('/'):
            return result[3:-1]
        else:
            return result[3:]
    else:
        return result


def deduct_http_url(url: str, as_https=True) -> str:
    if url.startswith('https://') or url.startswith('http://'):
        return url
    else:
        trailing_slash = None
        if url.endswith('/'):
            trailing_slash = ''
        else:
            trailing_slash = '/'
        if as_https:
            return 'https://' + url + trailing_slash
        else:
            return 'http://' + url + trailing_slash

    """
    if grammatically_correct(url):
        if as_https:
            return 'https://' + url +'/'
        else:
            return 'http://' + url + '/'
    else:
        raise InvalidUrlError(url)
    """
