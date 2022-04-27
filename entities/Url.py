from urllib.parse import urlparse, ParseResult
from entities.DomainName import DomainName
from entities.SchemeUrl import SchemeUrl
from exceptions.InvalidUrlError import InvalidUrlError


class Url:
    """
    This class represents an URL without scheme.

    ...

    Attributes
    ----------
    parse_result : ParseResult
        ParseResult object from the input string given in the initialization.
    """
    def __init__(self, input_string: str):
        """
        Initialize the object.

        :param input_string: The input string.
        :type input_string: str
        """
        if not input_string.startswith(('http://', 'https://', 'ftp://', 'ftps://')):
            string = 'https://' + input_string
            self._input_string_ = input_string
        else:
            string = input_string
            self._input_string_ = None
        if string.endswith('/'):
            string = string[0:-1]
        else:
            pass
        try:
            self.parse_result = urlparse(string)
        except ValueError:
            raise InvalidUrlError(string)
        temp = ParseResult(scheme='', netloc=self.parse_result.netloc, path=self.parse_result.path,
                           params=self.parse_result.params, query=self.parse_result.query,
                           fragment=self.parse_result.fragment)
        self._second_component_ = temp.geturl()[2:]
        temp = ParseResult(scheme='https', netloc=self.parse_result.netloc, path=self.parse_result.path,
                           params=self.parse_result.params, query=self.parse_result.query,
                           fragment=self.parse_result.fragment)
        self._https_ = temp.geturl() + '/'
        temp = ParseResult(scheme='http', netloc=self.parse_result.netloc, path=self.parse_result.path,
                           params=self.parse_result.params, query=self.parse_result.query,
                           fragment=self.parse_result.fragment)
        self._http_ = temp.geturl() + '/'
        self._domain_name_ = self.parse_result.netloc

    def http(self) -> SchemeUrl:
        """
        Returns the current URL with HTTP scheme.

        :return: The URL with HTTP scheme.
        :rtype: SchemeUrl
        """
        return SchemeUrl(self._http_)

    def https(self) -> SchemeUrl:
        """
        Returns the current URL with HTTPS scheme.

        :return: The URL with HTTPS scheme.
        :rtype: SchemeUrl
        """
        return SchemeUrl(self._https_)

    def second_component(self) -> str:
        """
        Returns second component of this URL as string.

        :return: The second component.
        :rtype: str
        """
        return self._second_component_

    def domain_name(self) -> DomainName:
        """
        Returns domain name of this UR.

        :return: The domain name.
        :rtype: DomainName
        """
        return DomainName(self._domain_name_)

    def original(self) -> str:
        """
        Returns the input string used during initialization.

        :return: The input string.
        :rtype: str
        """
        if self._input_string_ is None:
            raise ValueError
        else:
            return self._input_string_

    def __eq__(self, other) -> bool:
        """
        This method returns a boolean for comparing 2 objects equality.

        :param other:
        :return: The result of the comparison.
        :rtype: bool
        """
        if isinstance(other, Url):
            return self._second_component_ == other._second_component_
        else:
            return False

    def __str__(self) -> str:
        """
        This method returns a human-readable string representation of this object.

        :return: A human-readable string representation of this object.
        :rtype: str
        """
        return self._second_component_

    def __hash__(self) -> int:
        """
        This method returns the hash of this object. Should be defined alongside the __eq__ method with the same
        returning value from 2 objects.

        :return: Hash of this object.
        :rtype: int
        """
        return hash(self._second_component_)
