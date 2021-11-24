from typing import List


def multiple_contains(string_to_be_verified: str, strings: List[str]) -> bool:
    """
    Control if in a string there is at least one occurrence of one of the strings contained in the list parameter.

    :param string_to_be_verified: The string to be verified.
    :type string_to_be_verified: str
    :param strings: List of all the string parameters.
    :type strings: List[str]
    :return: True or false.
    :rtype: bool
    """
    for string in strings:
        if string in string_to_be_verified:
            return True
        else:
            pass
    return False
