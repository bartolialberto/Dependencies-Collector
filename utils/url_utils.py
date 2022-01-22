from urllib.parse import urlparse
from exceptions.InvalidUrlError import InvalidUrlError


def grammatically_correct(url: str) -> None:
    """
    This method parses a string to check if it is a valid URL. If it does, the method does nothing otherwise it raises
    an exception.

    :param url: The URL candidate.
    :type url: str
    :raise InvalidUrlError: If it is not a valid URL.
    """
    try:
        parsed_url = urlparse(url)
    except ValueError:
        raise InvalidUrlError(url)


def is_grammatically_correct(url: str) -> bool:
    """
    This method parses a string to check if it is a valid URL. If it does, True is returned otherwise False.

    :param url: The URL candidate.
    :type url: str
    :return: A boolean that tells if result is positive or negative.
    :rtype: bool
    """
    try:
        parsed_url = urlparse(url)
    except ValueError:
        return False
    return True


def deduct_second_component(http_url: str) -> str:
    """
    This method takes a HTTP URL and returns the URL without scheme (second component).

    :param http_url: A HTTP URL.
    :type http_url: str
    :raise InvalidUrlError: If parameter it's not a valid URL.
    :return: The resulting second component of the parameter.
    :rtype: str
    """
    try:
        parsed_url = urlparse(http_url)
    except ValueError:
        raise InvalidUrlError(http_url)
    scheme = parsed_url.scheme
    result = http_url.replace(scheme, '')
    if result.startswith('://'):
        if result.endswith('/'):
            return result[3:-1]
        else:
            return result[3:]
    else:
        return result


def deduct_http_url(url: str, as_https=True) -> str:
    """
    This method takes a URL (only second component) and returns the HTTP URL using HTTPS or HTTP according to the
    as_https parameter.

    :param url: An URL (only second component).
    :type url: str
    :param as_https: A flag to set the scheme to HTTPS or HTTP.
    :type as_https: bool
    :return: The resulting HTTP URL from the parameter.
    :rtype: str
    """
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
