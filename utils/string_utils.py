import csv
from pathlib import Path
from typing import List
from utils import file_utils


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


def equals_ignore_case(string1: str, string2: str) -> bool:
    """
    This methods checks if 2 strings are equal ignoring case.

    :param string1: A string.
    :type string1: str
    :param string2: A string.
    :type string2: str
    :return: True or False.
    :rtype: bool
    """
    return string1.casefold() == string2.casefold()


def contains_ignore_case(string_container: str, string_to_be_checked: str) -> bool:
    """
    This methods checks if a string is contained in another ignoring case.

    :param string_container: The string in which the control is done.
    :type string_container: str
    :param string_to_be_checked: The string to be verified.
    :type string_to_be_checked: str
    :return: True or False.
    :rtype: bool
    """
    return string_to_be_checked.casefold() in string_container.casefold()


def multiple_contains_ignore_case(string_list: List[str], string_to_be_checked: str) -> bool:
    """
    Control if in a string there is at least one occurrence of one of the string contained in the list parameter.
    The check is done ignoring case.

    :param string_list:
    :type string_list: List[str]
    :param string_to_be_checked:
    :type string_to_be_checked: str
    :return: True or False.
    :rtype: bool
    """
    temp = list()
    for s in string_list:
        temp.append(s.casefold())
    return multiple_contains(string_to_be_checked.casefold(), temp)
