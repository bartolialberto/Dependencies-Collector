from typing import List
from utils import domain_name_utils, string_utils
from utils.domain_name_utils import eliminate_trailing_point


class DomainName:
    def __init__(self, string: str):
        # self.string = domain_name_utils.insert_trailing_point(string)
        self.input_string = string
        self.string = domain_name_utils.standardize_for_application(string)

    def parse_subdomains(self, root_included: bool, tld_included: bool, self_included: bool) -> List['DomainName']:
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
        return self.string

    def __eq__(self, other) -> bool:
        if isinstance(other, DomainName):
            return string_utils.equals_ignore_case(eliminate_trailing_point(self.string), eliminate_trailing_point(other.string))
        elif isinstance(other, str):
            return string_utils.equals_ignore_case(eliminate_trailing_point(self.string), eliminate_trailing_point(other))
        else:
            return False

    def __iter__(self):
        return self.string.__iter__()

    def __next__(self):
        return self.string.__iter__().__next__()

    def __hash__(self) -> int:
        return hash(self.string)

    @staticmethod
    def from_string_list(strings: List[str]) -> List['DomainName']:
        result = list()
        for string in strings:
            result.append(DomainName(string))
        return result
