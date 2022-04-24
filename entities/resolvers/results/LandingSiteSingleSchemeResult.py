from typing import List
from entities.SchemeUrl import SchemeUrl
from entities.paths.APath import APath


class LandingSiteSingleSchemeResult:
    """
    This class represents the result of a single landing resolution using one scheme (HTTP or HTTPS).
    In short words is a wrapper for a collection of information.

    ...

    Attributes
    ----------
    url : SchemeUrl
        The landing URL (with scheme).
    redirection_path : List[str]
        The list of pages URL redirection.
    hsts : bool
        The presence of Strict-Transport-Security policy only in the landing page.
    a_path : APath
        The Path object that represents the domain name associated with the landing url.
    server : DomainName
        The domain name associated with the landing url.
    """
    def __init__(self, url: SchemeUrl, redirection_path: List[str], hsts: bool, a_path: APath):
        self.url = url
        self.redirection_path = redirection_path
        self.hsts = hsts
        self.a_path = a_path
        self.server = url.domain_name()
