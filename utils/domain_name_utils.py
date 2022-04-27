def standardize_for_application(string: str) -> str:
    """
    This method returns the predefined syntactic version of a string that represents a domain name in the project.
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

