from typing import List
from entities.error_log.ErrorLog import ErrorLog
from entities.resolvers.results.LandingSiteSingleSchemeResult import LandingSiteSingleSchemeResult


class LandingSiteResult:
    """
    This class represents the result of landing resolving, in particular it keeps track of the resolution computed
    through HTTP and HTTPS. In the end it keeps a list of error logs occurred during resolving.
    None is used if a landing cannot be executed or there's a problem (or even it is impossible because not supported).

    ...

    Attributes
    ----------
    https : Optional[LandingSiteSingleSchemeResult]
        The result of the HTTPS landing.
    http : Optional[LandingSiteSingleSchemeResult]
        The result of the HTTP landing.
    error_logs : List[ErrorLog]
        A list of error logs occurred during landing.
    """
    def __init__(self, https_result: LandingSiteSingleSchemeResult or None, http_result: LandingSiteSingleSchemeResult or None, error_logs: List[ErrorLog]):
        """
        Initialize object.

        :param https_result: The landing result using HTTPS scheme.
        :type https_result: Optional[LandingSiteSingleSchemeResult]
        :param http_result: The landing result using HTTP scheme.
        :type http_result: Optional[LandingSiteSingleSchemeResult]
        :param error_logs: The error logs list.
        :type error_logs: List[ErrorLog]
        """
        self.https = https_result
        self.http = http_result
        self.error_logs = error_logs
