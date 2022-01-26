from enum import Enum


class ServerTypes(Enum):
    """
    This class represents all server types that are concerned in this application. In particular this enumeration is
    needed as an auxiliary object to carry in the application flow together with the server string.

    """
    NAMESERVER = "NAMESERVER",
    WEBSERVER = "NS",
    SCRIPTSERVER = "SCRIPTSERVER",
    WEB_AND_SCRIPT_SERVER = "WEB_AND_SCRIPT_SERVER",

    def to_string(self) -> str:
        """
        This method returns a string representation of the type.

        :returns: The string representation of the type.
        :rtype: str
        """
        return self.value[0]

