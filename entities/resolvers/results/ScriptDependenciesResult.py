from typing import Set, Optional
from entities.MainFrameScript import MainFrameScript


class ScriptDependenciesResult:
    """
    This class represents the result of a web site script dependencies resolution.
    This means that this class is a simple wrapper for the script which the web site depends upon both using HTTPS
    scheme and HTTP scheme. None is used if connection using that scheme was impossible.

    ...

    Attributes
    ----------
    https : Union[Set[MainFrameScript], None]
        All the script that the web site depends upon using HTTPS scheme.
    http : Union[Set[MainPageScript], None]
        All the script that the web site depends upon using HTTP scheme.
    """
    def __init__(self, https_script_set: Optional[Set[MainFrameScript]], http_script_set: Optional[Set[MainFrameScript]]):
        """
        Initialize object.

        :param https_script_set: All the script that the web site depends upon using HTTPS scheme.
        :type https_script_set: Optional[Set[MainFrameScript]]
        :param http_script_set: All the script that the web site depends upon using HTTP scheme.
        :type http_script_set: Optional[Set[MainPageScript]]
        """
        self.https = https_script_set
        self.http = http_script_set
