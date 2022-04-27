from typing import List
from utils import domain_name_utils, string_utils
from utils.domain_name_utils import eliminate_trailing_point


class DomainName:
    """
    Class that represents a domain name with some helpful functionalities.

    ...

    Attributes
    ----------
    input_string : str
        The string used as input when instancing the object.
    string : str
        The standardized version of the input string. Standardized (for the application project) means 2 things:
            - every char is rendered lowercase
            - a trailing point is inserted (if it is not present)
    """
    def __init__(self, string: str):
        """
        Instantiate the object.

        :param string: The input string.
        :type string: str
        """
        self.input_string = string
        self.string = domain_name_utils.standardize_for_application(string)

    def parse_subdomains(self, root_included: bool, tld_included: bool, self_included: bool) -> List['DomainName']:
        """
        Method that parses every subdomains related to the self object (domain name). Some cases are not considered
        based on the boolean parameters.

        :param root_included: Flag that sets if the root zone should be considered.
        :type root_included: bool
        :param tld_included: Flag that sets if TLDs should be considered.
        :type tld_included: bool
        :param self_included: Flag that sets if self domain name should be considered.
        :type self_included: bool
        :return: The list of sub-domain names
        :rtype: List[DomainName]
        """
        if '@' in self.string:
            split = self.string.split('@')
            to_be_elaborated = split[-1]
        else:
            to_be_elaborated = self.string
        # limit case
        if root_included and self_included and self.string == '.':
            return [self]
        list_split = to_be_elaborated.split(".")
        to_be_elaborated = DomainName(to_be_elaborated)
        list_split.pop(len(list_split) - 1)
        subdomains = list()
        current_domain = "."
        subdomains.append(DomainName(current_domain))
        is_first = True
        for el in reversed(list_split):
            if is_first:
                current_domain = el + "."
                is_first = False
            else:
                current_domain = el + "." + current_domain
            subdomains.append(DomainName(current_domain))
        if not root_included:
            subdomains.pop(0)
        if not tld_included:
            subdomains = list(filter(lambda dn: not dn.is_tld(), subdomains))
        if not self_included:
            subdomains.remove(to_be_elaborated)
        return subdomains

    def construct_http_url(self, as_https: bool) -> str:
        """
        Generate HTTP URL associated to the domain name.

        :param as_https: Flag that sets if the URL scheme is HTTP or HTTPS.
        :type as_https: bool
        :return: The URL string.
        :rtype: str
        """
        temp = eliminate_trailing_point(self.string)
        if temp.startswith("www."):
            if as_https:
                return "https://" + temp + "/"
            else:
                return "http://" + temp + "/"
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

    def is_tld(self) -> bool:
        """
        Method that computes if this domain name is TLD.

        :return: True or False.
        :rtype: bool
        """
        if self.string == '.':
            return True
        point_count = self.string.count('.')
        if point_count == 0:
            return True
        elif point_count == 1:
            split_domain_name = self.string.split('.')
            if split_domain_name[0] != '' and split_domain_name[1] == '':
                return True
            elif split_domain_name[0] == '' and split_domain_name[1] != '':
                return True
            else:
                return False
        else:
            return False

    def __str__(self) -> str:
        """
        This method returns a human-readable string representation of this object.

        :return: A human-readable string representation of this object.
        :rtype: str
        """
        return self.string

    def __eq__(self, other) -> bool:
        """
        This method returns a boolean for comparing 2 objects equality.

        :param other:
        :return: The result of the comparison.
        :rtype: bool
        """
        if isinstance(other, DomainName):
            return string_utils.equals_ignore_case(eliminate_trailing_point(self.string), eliminate_trailing_point(other.string))
        elif isinstance(other, str):
            return string_utils.equals_ignore_case(eliminate_trailing_point(self.string), eliminate_trailing_point(other))
        else:
            return False

    def __iter__(self):
        """
        Class is iterable through the standardized string.

        :return: The iterator.
        :rtype: Iterator[str]
        """
        return self.string.__iter__()

    def __next__(self):
        """
        Class is iterable through the standardized string.

        :return: The next character of the standardized string.
        :rtype: str
        """
        return self.string.__iter__().__next__()

    def __hash__(self) -> int:
        """
        This method returns the hash of this object. Should be defined alongside the __eq__ method with the same
        returning value from 2 objects.

        :return: Hash of this object.
        :rtype: int
        """
        return hash(self.string)

    @staticmethod
    def from_string_list(strings: List[str]) -> List['DomainName']:
        """
        Static method that constructs a list of DomainName object from a list of strings.

        :param strings: A list of strings.
        :type strings: List[str]
        :return: A list of DomainName objects.
        :rtype: List[DomainName]
        """
        result = list()
        for string in strings:
            result.append(DomainName(string))
        return result
