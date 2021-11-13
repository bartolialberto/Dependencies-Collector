import csv
import re
from pathlib import Path
from typing import List
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

    :param domain_name: The candidate domain name.
    :type domain_name: str
    :return: True or False depending on the fact that is valid or not.
    :rtype: bool
    """
    pattern = re.compile('^([A-Za-z0-9]\\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\\.){1,3}[A-Za-z]{2,6}$')
    if re.match(pattern, domain_name):
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

    :param domain_name: The candidate domain name.
    :type domain_name: str
    :return: True or False depending on the fact that is valid or not.
    :rtype: bool
    """
    pattern = re.compile('^([A-Za-z0-9]\\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\\.){1,3}[A-Za-z]{2,6}$')
    if re.match(pattern, domain_name):
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


# TODO: se finisce con un punto???
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
                return "https://www."+temp+"/"
            else:
                return "http://www."+temp+"/"
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
        return domain_name


def insert_trailing_point(domain_name: str) -> str:
    """
    Method that inserts a single point character at the end of the string parameter.


    :param domain_name: The domain name.
    :type domain_name: str
    :return: The result.
    :rtype: str
    """
    if domain_name.endswith("."):
        return domain_name
    else:
        return domain_name+"."


# TODO: nessuna eccezione???
def deduct_domain_name(url: str) -> str:
    """
    Method that tries to isolate a valid domain name from the url string parameter given.


    :param url: The url.
    :type url: str
    :return: The deducted domain name.
    :rtype: str
    """
    # temp = url.replace("www.", "")
    temp = url
    if temp.endswith("/"):
        temp = temp[0:-1]
    last_point_index = temp.rindex(".")
    end_index = -1
    for i, char in enumerate(temp, start=last_point_index):
        if i == '/':
            end_index = i
    if end_index == -1:
        pass
    else:
         temp = temp[:end_index]
    if temp.startswith("http://"):
        temp = temp.replace("http://", "")
        return temp
    elif temp.startswith("https://"):
        temp = temp.replace("https://", "")
        return temp
    elif temp.startswith("ftp://"):
        temp = temp.replace("ftp://", "")
        return temp
    elif temp.startswith("ftps://"):
        temp = temp.replace("ftps://", "")
        return temp
    else:
        return temp


def take_snapshot(domain_name_list: List[str]):
    file = file_utils.set_file_in_folder("SNAPSHOTS", "temp_domain_names.csv")
    if not file.exists():
        pass
    with file.open('w', encoding='utf-8', newline='') as f:
        write = csv.writer(f)
        for domain_name in domain_name_list:
            write.writerow([domain_name])
        f.close()
