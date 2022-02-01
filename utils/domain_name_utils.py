import re
from typing import List
from urllib.parse import urlparse
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from utils import string_utils, url_utils


# TODO: method doesn't work for 'c.ns.c10r.facebook.com.' ==> MUST BE MODIFIED OR DELETED
def grammatically_correct(domain_name: str) -> None:
    """
    Method that validate a string representating a domain name, using these rules:
        - the domain name should be a-z or A-Z or 0-9 and hyphen (-).
        - the domain name should be between 1 and 63 characters long.
        - the domain name should not start or end with a hyphen(-) (e.g. -geeksforgeeks.org or geeksforgeeks.org-).
        - the last TLD (Top level domain) must be at least two characters and a maximum of 6 characters.
        - the domain name can be a subdomain (e.g. contribute.geeksforgeeks.org)
    Also, it is considered valid even with the trailing point.

    :param domain_name: The candidate domain name.
    :type domain_name: str
    :return: True or False depending on the fact that is valid or not.
    :rtype: bool
    """
    # original: '^([A-Za-z0-9]\\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\\.){1,3}[A-Za-z]{2,6}$'
    temp = eliminate_trailing_point(domain_name)
    pattern = re.compile('^([A-Za-z0-9]\\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\\.){1,3}[A-Za-z]{2,6}$')
    if re.match(pattern, temp):
        pass
    else:
        raise InvalidDomainNameError(domain_name)


def is_grammatically_correct(domain_name: str) -> bool:
    """
    Method that validate a string representating a domain name, using these rules:
        - the domain name should be a-z or A-Z or 0-9 and hyphen (-).
        - the domain name should be between 1 and 63 characters long.
        - the domain name should not start or end with a hyphen(-) (e.g. -geeksforgeeks.org or geeksforgeeks.org-).
        - the last TLD (Top level domain) must be at least two characters and a maximum of 6 characters.
        - the domain name can be a subdomain (e.g. contribute.geeksforgeeks.org)
    Also, it is considered valid even with the trailing point.

    :param domain_name: The candidate domain name.
    :type domain_name: str
    :return: True or False depending on the fact that is valid or not.
    :rtype: bool
    """
    temp = eliminate_trailing_point(domain_name)
    pattern = re.compile('^([A-Za-z0-9]\\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\\.){1,3}[A-Za-z]{2,6}$')
    if re.match(pattern, temp):
        return True
    else:
        return False


def get_subdomains_name_list(domain: str, root_included=False, parameter_included=True) -> List[str]:
    """
    Method that gives all the subdomain name from a domain name. An example:
        'www.units.it' ---> ['it.', 'units.it.', 'www.units.it.']
    The trailing point is added if absent.
    In particular this method handles even email addresses.


    :param domain: The domain name.
    :type domain: str
    :param root_included: Optional boolean to decide if the root domain has to be returned.
    :type root_included: bool
    :param parameter_included: Optional boolean to decide if the domain parameter has to be returned.
    :type parameter_included: bool
    :return: The list containing all subdomains' domain name.
    :rtype: list[str]
    """
    if '@' in domain:
        split = domain.split('@')
        return inner_subdomains_parser(split[-1], root_included=root_included, parameter_included=parameter_included)
    else:
        return inner_subdomains_parser(domain, root_included=root_included, parameter_included=parameter_included)


def inner_subdomains_parser(domain: str, root_included=False, parameter_included=True) -> List[str]:
    """
    Method that gives all the subdomain name from a domain name. An example:
        'www.units.it' ---> ['it.', 'units.it.', 'www.units.it.']
    The trailing point is added if absent.
    In particular this method does the elaboration handling 'pure' domain names, not email addresses.


    :param domain: The domain name.
    :type domain: str
    :param root_included: Optional boolean to decide if the root domain has to be returned.
    :type root_included: bool
    :param parameter_included: Optional boolean to decide if the domain parameter has to be returned.
    :type parameter_included: bool
    :return: The list containing all subdomains' domain name.
    :rtype: list[str]
    """
    domain_name = insert_trailing_point(domain)
    list_split = domain_name.split(".")
    list_split.pop(len(list_split) - 1)
    subdomains = list()
    current_domain = "."
    subdomains.append(current_domain)
    is_first = True
    for el in reversed(list_split):
        if is_first:
            current_domain = el + "."
            is_first = False
        else:
            current_domain = el + "." + current_domain
        subdomains.append(current_domain)
    if not root_included:
        subdomains.pop(0)
    if not parameter_included:
        subdomains.remove(domain)
    return subdomains


def deduct_http_url(domain_name: str, as_https=True) -> str:
    """
    Method that tries to construct a http/https url from the domain name only.


    :param domain_name: The domain name.
    :type domain_name: str
    :param as_https: Optional boolean to decide if the url scheme is https or http.
    :type as_https: bool
    :raise raiseInvalidDomainNameError: If the domain name is not valid.
    :return: The deducted url.
    :rtype: str
    """
    temp = eliminate_trailing_point(domain_name)
    if temp.startswith("www."):
        if as_https:
            return "https://"+temp+"/"
        else:
            return "http://"+temp+"/"
    elif temp.startswith("https://"):
        if as_https:
            return temp
        else:
            return temp.replace("https://", "http://")
    elif temp.startswith("http://"):
        if as_https:
            return temp.replace("http://", "https://")
        else:
            return temp
    else:
        if as_https:
            return "https://" + temp + "/"
        else:
            return "http://" + temp + "/"
        """
        if is_grammatically_correct(temp):
            if as_https:
                return "https://"+temp+"/"
            else:
                return "http://"+temp+"/"
        else:
            raise InvalidDomainNameError(temp)
        """


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


def multiple_contains(domain_names: List[str], domain_name_to_be_verified: str) -> bool:
    """
    Control if in a domain name there is at least one occurrence of one of the domain names contained in the list
    parameter. The check is done considering the strings' case and the trailing point.

    :param domain_names: List of all the domain name parameters.
    :type domain_names: List[str]
    :param domain_name_to_be_verified: The domain name to be verified.
    :type domain_name_to_be_verified: str
    :return: True or False.
    :rtype: bool
    """
    for string in domain_names:
        if contains(string, domain_name_to_be_verified):
            return True
        else:
            pass
    return False


def is_contained_in_list(domain_names: List[str], domain_name: str) -> bool:
    """
    Returns if a domain name is contained exactly in a list of domain names, taking care about the trailing point and the
    case when comparing.


    :param domain_names: A list of domain names.
    :type domain_names: List[str]
    :param domain_name: A domain name.
    :type domain_name: str
    :returns: True or False
    :rtype: bool
    """
    for dn in domain_names:
        if equals(domain_name, dn):
            return True
    return False
