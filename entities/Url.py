from urllib.parse import urlparse, ParseResult
from entities.DomainName import DomainName
from entities.SchemeUrl import SchemeUrl
from exceptions.InvalidUrlError import InvalidUrlError


class Url:
    def __init__(self, input_string: str):
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
        return SchemeUrl(self._http_)

    def https(self) -> SchemeUrl:
        return SchemeUrl(self._https_)

    def second_component(self) -> str:
        return self._second_component_

    def domain_name(self) -> DomainName or str:
        return DomainName(self._domain_name_)

    def original(self) -> str:
        if self._input_string_ is None:
            raise ValueError
        else:
            return self._input_string_

    def __eq__(self, other) -> bool:
        if isinstance(other, Url):
            return self._second_component_ == other._second_component_
        else:
            return False

    def __str__(self) -> str:
        return self._second_component_

    def __hash__(self) -> int:
        return hash(self._second_component_)
