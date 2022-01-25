from enum import Enum


# TODO: docs
class ServerTypes(Enum):
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

