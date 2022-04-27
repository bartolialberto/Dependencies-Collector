def equals_ignore_case(string1: str, string2: str) -> bool:
    """
    Static method that checks if 2 strings are equal ignoring case.

    :param string1: A string.
    :type string1: str
    :param string2: A string.
    :type string2: str
    :return: True or False.
    :rtype: bool
    """
    return string1.casefold() == string2.casefold()


def stamp_https_from_bool(is_https: bool) -> str:
    """
    Static method that prints 'HTTP' or 'HTTPS' based on a boolean value.

    :param is_https: A boolean value.
    :type is_https: bool
    :return: 'HTTPS' or 'HTTP'
    :rtype: str
    """
    if is_https:
        return 'HTTPS'
    else:
        return 'HTTP'
