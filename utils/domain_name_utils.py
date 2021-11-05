import re


# return list with higher domain names first in the list
def get_subdomains_name_list(domain_name: str, root_included=False):
    check = re.findall("[/@,#]", domain_name)
    if len(check) != 0:
        print(domain_name, " is not a valid domain.")
        return None
    if not domain_name.endswith("."):
        domain_name = domain_name + "."
    else:
        pass
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
