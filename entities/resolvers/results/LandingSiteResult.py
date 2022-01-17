from ipaddress import IPv4Address
from typing import List
from entities.error_log.ErrorLog import ErrorLog
from utils import domain_name_utils


class InnerLandingSiteSingleSchemeResult:
    """
    This class represents the result of a single landing resolution using one scheme (generally HTTP or HTTPS).
    In short words is a wrapper for a collection of information.

    ...

    Attributes
    ----------
    url : str
        The landing URL (with scheme).
    redirection_path : List[str]
        The list of pages URL redirection.
    hsts : bool
        The presence of Strict-Transport-Security policy in the landing page.
    ip : ipaddress.IPv4Address
        The IP address.
    server : str
        The landing URL (without scheme).
    """
    def __init__(self, url: str, redirection_path: List[str], hsts: bool, ip: IPv4Address):
        self.url = url
        self.redirection_path = redirection_path
        self.hsts = hsts
        self.ip = ip
        self.server = domain_name_utils.deduct_domain_name(url)


class LandingSiteResult:
    """
    This class represents the result of landing resolving, in particular it keeps track of the resolution computed
    through HTTP and HTTPS. In the end it keeps a list of error logs occurred during resolving.
    None is used if a landing cannot be executed or there's a problem (or even it is impossible because not supported).

    ...

    Attributes
    ----------
    https : InnerLandingSiteSingleSchemeResult
        The result of the HTTPS landing.
    http : InnerLandingSiteSingleSchemeResult
        The result of the HTTP landing.
    error_logs : List[ErrorLog]
        A list of error logs occurred during landing.
    """
    def __init__(self, https_result: InnerLandingSiteSingleSchemeResult or None, http_result: InnerLandingSiteSingleSchemeResult or None, error_logs: List[ErrorLog]):
        """
        Initialize object.

        :param https_result: The landing result using HTTPS scheme.
        :type https_result: InnerLandingSiteSingleSchemeResult or None
        :param http_result: The landing result using HTTP scheme.
        :type http_result: InnerLandingSiteSingleSchemeResult or None
        :param error_logs: The error logs list.
        :type error_logs: List[ErrorLog]
        """
        self.https = https_result
        self.http = http_result
        self.error_logs = error_logs
