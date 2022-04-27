from urllib.parse import urlparse, ParseResult
from entities.DomainName import DomainName
from exceptions.InvalidUrlError import InvalidUrlError


class SchemeUrl:
    """
    This class represents an URL with scheme (HTTP or HTTPS).

    ...

    Attributes
    ----------
    string : str
        Input string used to create this object.
    parse_result : ParseResult
        ParseResult object from the input string.
    """
    def __init__(self, string: str):
        """
        Initialize the object.

        :param string: The input string.
        :type string: str
        """
        if not string.startswith('https') and not string.startswith('http'):
            raise ValueError
        self.string = string
        try:
            self.parse_result = urlparse(string)
        except ValueError:
            raise InvalidUrlError(string)
        temp = ParseResult(scheme='', netloc=self.parse_result.netloc, path=self.parse_result.path,
                           params=self.parse_result.params, query=self.parse_result.query,
                           fragment=self.parse_result.fragment)
        self._second_component_ = temp.geturl()[2:]
        self._domain_name_ = self.parse_result.netloc

    def is_http(self) -> bool:
        """
        It returns a boolean saying if this URL's scheme is HTTP.

        :return: True if scheme is HTTP, False otherwise.
        :rtype: bool
        """
        return self.parse_result.scheme == 'http'

    def is_https(self) -> bool:
        """
        It returns a boolean saying if this URL's scheme is HTTPS.

        :return: True if scheme is HTTPS, False otherwise.
        :rtype: bool
        """
        return self.parse_result.scheme == 'https'

    def stamp_landing_scheme(self) -> str:
        """
        Returns a string based on the scheme.

        :return: 'HTTPS' if scheme is HTTPS, 'HTTP' otherwise.
        :rtype: str
        """
        if self.is_https():
            return 'HTTPS'
        elif self.is_http():
            return 'HTTP'
        else:
            raise ValueError

    def second_component(self) -> str:
        """
        Returns the second component associated to this URL as string.

        :return: Second component.
        :rtype: str
        """
        return self._second_component_

    def domain_name(self) -> DomainName:
        """
        Returns the domain name associated to this URL.

        :return: Domain name associated to this URL.
        :rtype: DomainName
        """
        return DomainName(self._domain_name_)

    def __eq__(self, other) -> bool:
        """
        This method returns a boolean for comparing 2 objects equality.

        :param other:
        :return: The result of the comparison.
        :rtype: bool
        """
        if isinstance(other, SchemeUrl):
            return self.string == other.string
        else:
            return False

    def __str__(self) -> str:
        """
        This method returns a human-readable string representation of this object.

        :return: A human-readable string representation of this object.
        :rtype: str
        """
        return self.string

    def __hash__(self) -> int:
        """
        This method returns the hash of this object. Should be defined alongside the __eq__ method with the same
        returning value from 2 objects.

        :return: Hash of this object.
        :rtype: int
        """
        return hash(self.string)
