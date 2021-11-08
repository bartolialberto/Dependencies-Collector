import re
from exceptions.InvalidDomainNameError import InvalidDomainNameError


# The domain name should be a-z or A-Z or 0-9 and hyphen (-).
# The domain name should be between 1 and 63 characters long.
# The domain name should not start or end with a hyphen(-) (e.g. -geeksforgeeks.org or geeksforgeeks.org-).
# The last TLD (Top level domain) must be at least two characters and a maximum of 6 characters.
# The domain name can be a subdomain (e.g. contribute.geeksforgeeks.org)
def grammatically_correct(domain_name: str):
    pattern = re.compile('^([A-Za-z0-9]\\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\\.){1,3}[A-Za-z]{2,6}$')
    if re.match(pattern, domain_name):
        pass
    else:
        raise InvalidDomainNameError(domain_name)


def is_grammatically_correct(domain_name: str) -> bool:
    pattern = re.compile('^([A-Za-z0-9]\\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\\.){1,3}[A-Za-z]{2,6}$')
    if re.match(pattern, domain_name):
        return True
    else:
        return False


# return list with higher domain names first in the list
def get_subdomains_name_list(domain_name: str, root_included=False):
    if not domain_name.endswith("."):
        domain_name = domain_name + "."
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


def deduct_url(domain_name: str, as_https=True):
    if domain_name.startswith("www."):
        if as_https:
            return "https://"+domain_name+"/"
        else:
            return "http://"+domain_name+"/"
    elif domain_name.startswith("https://"):
        if as_https:
            return domain_name
        else:
            return domain_name.replace("https://", "http://")
    elif domain_name.startswith("http://"):
        if as_https:
            return domain_name.replace("http://", "https://")
        else:
            return domain_name
    else:
        if is_grammatically_correct(domain_name):
            if as_https:
                return "https://www."+domain_name+"/"
            else:
                return "http://www."+domain_name+"/"
        else:
            raise InvalidDomainNameError(domain_name)
