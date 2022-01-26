from enum import Enum


class ResolvingErrorCauses(Enum):
    """
    This class represents all the causes' enumeration that brings about unresolved entities.
    The value associated is an integer but that it's irrelevant.

    """
    NAME_SERVER_WITHOUT_ACCESS_PATH = 1,
    NO_HTTPS_LANDING_FOR_WEB_SITE = 2,
    NO_HTTP_LANDING_FOR_WEB_SITE = 3,
    NO_HTTPS_LANDING_FOR_SCRIPT_SITE = 4,
    NO_HTTP_LANDING_FOR_SCRIPT_SITE = 5,
    INCOMPLETE_DEPENDENCIES_FOR_ADDRESS = 6,
    IMPOSSIBLE_TO_WITHDRAW_SCRIPT = 7,      # TODO

    def __str__(self):
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        if self == ResolvingErrorCauses.NAME_SERVER_WITHOUT_ACCESS_PATH:
            return 'NAME_SERVER_WITHOUT_ACCESS_PATH'
        elif self == ResolvingErrorCauses.NO_HTTPS_LANDING_FOR_WEB_SITE:
            return 'NO_HTTPS_LANDING_FOR_WEB_SITE'
        elif self == ResolvingErrorCauses.NO_HTTP_LANDING_FOR_WEB_SITE:
            return 'NO_HTTP_LANDING_FOR_WEB_SITE'
        elif self == ResolvingErrorCauses.NO_HTTPS_LANDING_FOR_SCRIPT_SITE:
            return 'NO_HTTPS_LANDING_FOR_SCRIPT_SITE'
        elif self == ResolvingErrorCauses.NO_HTTP_LANDING_FOR_SCRIPT_SITE:
            return 'NO_HTTP_LANDING_FOR_SCRIPT_SITE'
        elif self == ResolvingErrorCauses.INCOMPLETE_DEPENDENCIES_FOR_ADDRESS:
            return 'INCOMPLETE_DEPENDENCIES_FOR_ADDRESS'
        elif self == ResolvingErrorCauses.IMPOSSIBLE_TO_WITHDRAW_SCRIPT:
            return 'IMPOSSIBLE_TO_WITHDRAW_SCRIPT'
        else:
            raise ValueError
