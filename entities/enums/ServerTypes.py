from enum import Enum


class ServerTypes(Enum):
    """
    This class represents all server types that are concerned in this application. In particular this enumeration is
    needed as an auxiliary object to carry in the application flow together with the server string.

    """
    NAMESERVER = "NAME SERVER",
    WEBSERVER = "WEB SERVER",
    SCRIPTSERVER = "SCRIPT SERVER",
    MAIL_SERVER = "MAIL SERVER",
    WEB_AND_SCRIPT_SERVER = "WEB AND SCRIPT SERVER",
    NAME_AND_WEB_SERVER = "NAME AND WEB SERVER",
    NAME_AND_SCRIPT_SERVER = "NAME AND SCRIPT SERVER",
    NAME_AND_SCRIPT_AND_WEB_SERVER = "NAME AND SCRIPT AND WEB SERVER",

    def to_string(self) -> str:
        """
        This method returns a string representation of the type.

        :returns: The string representation of the type.
        :rtype: str
        """
        return self.value[0]

    @staticmethod
    def parse_multiple_types(type_1: 'ServerTypes', type_2: 'ServerTypes') -> 'ServerTypes':
        if type_1 == type_2:
            return type_1
        elif (type_1 == ServerTypes.WEBSERVER and type_2 == ServerTypes.SCRIPTSERVER) or (type_1 == ServerTypes.SCRIPTSERVER and type_2 == ServerTypes.WEBSERVER):
            return ServerTypes.WEB_AND_SCRIPT_SERVER
        elif (type_1 == ServerTypes.SCRIPTSERVER and type_2 == ServerTypes.NAMESERVER) or (type_1 == ServerTypes.NAMESERVER and type_2 == ServerTypes.SCRIPTSERVER):
            return ServerTypes.NAME_AND_SCRIPT_SERVER
        elif (type_1 == ServerTypes.WEBSERVER and type_2 == ServerTypes.NAMESERVER) or (type_1 == ServerTypes.NAMESERVER and type_2 == ServerTypes.WEBSERVER):
            return ServerTypes.NAME_AND_WEB_SERVER

        elif (type_1 == ServerTypes.WEB_AND_SCRIPT_SERVER and type_2 == ServerTypes.WEBSERVER) or (type_1 == ServerTypes.WEBSERVER and type_2 == ServerTypes.WEB_AND_SCRIPT_SERVER):
            return ServerTypes.WEB_AND_SCRIPT_SERVER
        elif (type_1 == ServerTypes.WEB_AND_SCRIPT_SERVER and type_2 == ServerTypes.SCRIPTSERVER) or (type_1 == ServerTypes.SCRIPTSERVER and type_2 == ServerTypes.WEB_AND_SCRIPT_SERVER):
            return ServerTypes.WEB_AND_SCRIPT_SERVER
        elif (type_1 == ServerTypes.NAME_AND_SCRIPT_SERVER and type_2 == ServerTypes.NAMESERVER) or (type_1 == ServerTypes.NAMESERVER and type_2 == ServerTypes.NAME_AND_SCRIPT_SERVER):
            return ServerTypes.NAME_AND_SCRIPT_SERVER
        elif (type_1 == ServerTypes.NAME_AND_SCRIPT_SERVER and type_2 == ServerTypes.SCRIPTSERVER) or (type_1 == ServerTypes.SCRIPTSERVER and type_2 == ServerTypes.NAME_AND_SCRIPT_SERVER):
            return ServerTypes.NAME_AND_SCRIPT_SERVER
        elif (type_1 == ServerTypes.NAME_AND_WEB_SERVER and type_2 == ServerTypes.NAMESERVER) or (type_1 == ServerTypes.NAMESERVER and type_2 == ServerTypes.NAME_AND_WEB_SERVER):
            return ServerTypes.NAME_AND_WEB_SERVER
        elif (type_1 == ServerTypes.NAME_AND_WEB_SERVER and type_2 == ServerTypes.WEBSERVER) or (type_1 == ServerTypes.WEBSERVER and type_2 == ServerTypes.NAME_AND_WEB_SERVER):
            return ServerTypes.NAME_AND_WEB_SERVER

        elif (type_1 == ServerTypes.NAME_AND_WEB_SERVER and type_2 == ServerTypes.NAME_AND_SCRIPT_SERVER) or (type_1 == ServerTypes.NAME_AND_SCRIPT_SERVER and type_2 == ServerTypes.NAME_AND_WEB_SERVER):
            return ServerTypes.NAME_AND_SCRIPT_AND_WEB_SERVER

        else:
            print('')
            pass

