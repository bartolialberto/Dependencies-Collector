import re
from exceptions.InvalidDomainNameError import InvalidDomainNameError


def grammatically_correct(address: str) -> None:
    """
    Method that validate a string representating an email address, using these rules:

    :param address: The candidate email address.
    :type address: str
    :raise InvalidDomainNameError: If the email address is not valid.
    """
    pattern = re.compile('\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\\b')
    if re.match(pattern, address):
        pass
    else:
        raise InvalidDomainNameError(address)


def is_grammatically_correct(address: str) -> bool:
    """
    Method that validate a string representating an email address, using these rules:

    :param address: The candidate email address.
    :type address: str
    :return: True or False depending on the fact that is valid or not.
    :rtype: bool
    """
    pattern = re.compile('\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\\b')
    if re.match(pattern, address):
        return True
    else:
        return False
