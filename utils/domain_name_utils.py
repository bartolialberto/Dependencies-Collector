import re
from typing import List
from urllib.parse import urlparse
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from utils import string_utils, url_utils


def standardize_for_application(string: str) -> str:
    """
    This method returns the predefined syntactic version of a string that represents a domain name in the system.
    This means taking a string that is supposed to represents a domain name, make it all lowercase and then adding
    a trailing point.

    :param string: A string.
    :type string: str
    :return: The result string.
    :rtype: str
    """
    return insert_trailing_point(string.strip().casefold())



def eliminate_trailing_point(domain_name: str) -> str:
    """
    Method that eliminates all trailing point in the string.


    :param domain_name: The domain name.
    :type domain_name: str
    :return: The domain name without any point character at the ending.
    :rtype: str
    """
    if domain_name.endswith("."):
        return eliminate_trailing_point(domain_name[:-1])
    else:
        return (domain_name+'.')[:-1]   # same string (DEEP COPY)


def insert_trailing_point(domain_name: str) -> str:
    """
    Method that inserts a single point character at the end of the string parameter.


    :param domain_name: The domain name.
    :type domain_name: str
    :return: The result.
    :rtype: str
    """
    if domain_name.endswith("."):
        return (domain_name+'.')[:-1]   # same string (DEEP COPY)
    else:
        return domain_name+"."


def deduct_domain_name(url: str, with_trailing_point=True) -> str:
    """
    Method that tries to isolate a valid domain name from the url string parameter given.


    :param url: The url.
    :type url: str
    :param with_trailing_point: The flag to set if domain name should have trailing point.
    :type with_trailing_point: bool
    :return: The deducted domain name.
    :rtype: str
    """
    parser = urlparse(url)
    domain_name = parser.netloc
    if domain_name == '':
        parser = urlparse(url_utils.deduct_http_url(url))
        domain_name = parser.netloc
    if with_trailing_point:
        return insert_trailing_point(domain_name)
    else:
        return domain_name


def equals(domain_name1: str, domain_name2: str) -> bool:
    """
    Return if 2 domain names (as string) are equals: this means if one of them (or all of them) has the trailing point,
    this method handles that. Also it ignores case.


    :param domain_name1: First domain name.
    :type domain_name1: str
    :param domain_name2: Second domain name.
    :type domain_name2: str
    :returns: True or False
    :rtype: bool
    """
    return string_utils.equals_ignore_case(eliminate_trailing_point(domain_name1), eliminate_trailing_point(domain_name2))


def contains(string_to_be_checked: str, string_container: str) -> bool:
    """
    This method checks if the first string parameter is contained in the second string parameter. The check is done
    considering the strings' case and the trailing point.

    :param string_to_be_checked: The string to be checked.
    :type string_to_be_checked: str
    :param string_container: The string in which the control is done.
    :type string_container: str
    :return: True or False.
    :rtype: bool
    """
    return eliminate_trailing_point(string_to_be_checked).casefold() in eliminate_trailing_point(string_container).casefold()


def is_tld(domain_name: str) -> bool:
    """
    This method returns a boolean if the string parameter is grammatically a TLD.

    :param domain_name: A domain name as string.
    :type domain_name: str
    :return: A boolean.
    :rtype: bool
    """
    if domain_name == '.':
        return True
    point_count = domain_name.count('.')
    if point_count == 0:
        return True
    elif point_count == 1:
        split_domain_name = domain_name.split('.')
        if split_domain_name[0] != '' and split_domain_name[1] == '':
            return True
        elif split_domain_name[0] == '' and split_domain_name[1] != '':
            return True
        else:
            return False
    else:
        return False

