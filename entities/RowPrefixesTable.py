import ipaddress
from entities.enums.ROVStates import ROVStates
from exceptions.NotROVStateTypeError import NotROVStateTypeError


class RowPrefixesTable:
    """
    This class represent a row of the pfx_table_div (id of html element) table in the page (ROV page):
            https://stats.labs.apnic.net/roa/ASXXXX?c=IT&l=1&v=4&t=thist&d=thisd
    where XXXX is the autonomous system number.

    ...

    Attributes
    ----------
    as_number : `int`
        The autonomous system number.
    prefix : `ipaddress.IPv4Network`
        The row prefix announced from the current autonomous system.
    span : `int`
        The span.
    cc : `str`
        The cc.
    visibility : `int`
        The visibility.
    rov_state : `ROVStates`
        The ROV state (UNKNOWN, INVALID, VALID).
    roas : `str`
        The ROAS.
    """
    def __init__(self, as_number: str, prefix: str, span: str, cc: str, visibility: str, rov_state: str, roas: str):
        """
        Initialize an object from a string representation of every attribute.

        :param as_number:
        :type as_number: str
        :param prefix:
        :type as_number: str
        :param span:
        :type span: str
        :param cc:
        :type cc: str
        :param visibility:
        :type visibility: str
        :param rov_state:
        :type rov_state: str
        :param roas:
        :type roas: str
        :raise ValueError: If as_number is not a parsable integer number or it's an integer number < 0.
        :raise ValueError: If prefix is not a valid string representation of a IPv4Network.
        :raise ValueError: If span is not a parsable integer number.
        :raise ValueError: If cc is a string with length != 2.
        :raise ValueError: If visibility is not a parsable integer number.
        :raise NotROVStateTypeError: If rov_state is not a parsable ROV state.
        """
        tmp = as_number.strip('AS')
        try:
            int_as_number = int(tmp)
        except ValueError:
            raise
        if int_as_number >= 0:
            self.as_number = int_as_number
        else:
            raise ValueError()
        try:
            self.prefix = ipaddress.ip_network(prefix)
        except ValueError:
            raise
        tmp = span.replace(',', '')
        try:
            int_span = int(tmp)
        except ValueError:
            raise
        if int_span >= 0:
            self.span = int_span
        else:
            raise ValueError()
        if len(cc) == 2:
            self.cc = cc
        else:
            raise ValueError()
        try:
            int_visibility = int(visibility)
        except ValueError:
            raise
        if int_visibility >= 0:
            self.visibility = int_visibility
        else:
            raise ValueError()
        try:
            enum_rov_state = ROVStates.parse_from_string(rov_state)
            self.rov_state = enum_rov_state
        except NotROVStateTypeError:
            raise
        self.roas = roas

    def __str__(self) -> str:
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        return f"[AS{self.as_number}\t{self.prefix.compressed}\t{str(self.span)}\t{self.cc}\t{str(self.visibility)}\t{self.rov_state.to_string()}\t{self.roas}]"