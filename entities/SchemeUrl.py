from urllib.parse import urlparse, ParseResult
from entities.DomainName import DomainName
from exceptions.InvalidUrlError import InvalidUrlError


class SchemeUrl:
    def __init__(self, string: str):
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
        return self.parse_result.scheme == 'http'

    def is_https(self) -> bool:
        return self.parse_result.scheme == 'https'

    def stamp_landing_scheme(self) -> str:
        if self.is_https():
            return 'HTTPS'
        elif self.is_http():
            return 'HTTP'
        else:
            raise ValueError

    def second_component(self) -> str:
        return self._second_component_

    def domain_name(self) -> DomainName:
        return DomainName(self._domain_name_)

    def __eq__(self, other) -> bool:
        if isinstance(other, SchemeUrl):
            return self.string == other.string
        else:
            return False

    def __str__(self) -> str:
        return self.string

    def __hash__(self) -> int:
        return hash(self.string)
