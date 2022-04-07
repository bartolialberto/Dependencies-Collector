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
