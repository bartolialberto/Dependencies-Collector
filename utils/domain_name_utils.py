import csv
import re
from typing import List
from urllib.parse import urlparse
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from utils import file_utils


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


# return list with higher domain names first in the list
def get_subdomains_name_list(domain: str, root_included=False) -> List[str]:
    """
    Method that gives all the subdomain name from a domain name. An example:
        'www.units.it' ---> ['it.', 'units.it.', 'www.units.it.']
    As you can see the trailing point is added if absent.


    :param domain: The domain name.
    :type domain: str
    :param root_included: Optional boolean to decide if the root domain has to be returned.
    :type root_included: bool
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
        if is_grammatically_correct(temp):
            if as_https:
                return "https://"+temp+"/"
            else:
                return "http://"+temp+"/"
        else:
            raise InvalidDomainNameError(temp)


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


def deduct_domain_name(url: str) -> str:
    """
    Method that tries to isolate a valid domain name from the url string parameter given.


    :param url: The url.
    :type url: str
    :return: The deducted domain name.
    :rtype: str
    """
    return urlparse(url).netloc


def take_snapshot(domain_name_list: List[str]) -> None:
    """
    Export the domain list as a .csv file in the SNAPSHOTS folder of the project root folder (PRD) with a predefined
    filename.


    :param domain_name_list: A list of domain name.
    :type domain_name_list: List[str]
    """
    file = file_utils.set_file_in_folder("SNAPSHOTS", "temp_domain_names.csv")
    if not file.exists():
        pass
    with file.open('w', encoding='utf-8', newline='') as f:
        write = csv.writer(f)
        for domain_name in domain_name_list:
            write.writerow([domain_name])
        f.close()


def equals(domain_name1: str, domain_name2: str) -> bool:
    """
    Return if 2 domain names (as string) are equals: this means if one of them (or all of them) has the trailing point
    this method handle that.


    :param domain_name1: First domain name.
    :type domain_name1: str
    :param domain_name2: Second domain name.
    :type domain_name2: str
    :returns: True or False
    :rtype: bool
    """
    tmp1 = eliminate_trailing_point(domain_name1)
    tmp2 = eliminate_trailing_point(domain_name2)
    return tmp1 == tmp2


def is_contained_in_list(_list: List[str], domain_name: str) -> bool:
    """
    Return if a domain name is contained in a list, taking care about the trailing point when comparing.


    :param _list: A list of domain names.
    :type _list: List[str]
    :param domain_name: A domain name.
    :type domain_name: str
    :returns: True or False
    :rtype: bool
    """
    for elem in _list:
        if equals(elem, domain_name):
            return True
    return False
