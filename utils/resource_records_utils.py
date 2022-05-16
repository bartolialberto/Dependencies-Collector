import ipaddress
from typing import List
from entities.DomainName import DomainName
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR


def stamp_values(type_rr: TypesRR, values: list) -> str:
    """
    Static method that returns a string representation of a list of the RR object values supported in this application;
    such objects are: DomainName and IPv4Address.

    :param type_rr: RR type.
    :type type_rr: TypesRR
    :param values: List of values.
    :type values: list
    :return: String representation.
    :rtype: str
    """
    if type_rr == TypesRR.A:
        str_values = list(map(lambda ia: ia.exploded, values))
        return str(str_values).replace('\'', '')
    elif type_rr == TypesRR.CNAME or type_rr == TypesRR.NS:
        str_values = list(map(lambda dn: dn.string, values))
        return str(str_values).replace('\'', '')
    elif type_rr == TypesRR.MX:
        str_values = list()
        for value in values:
            if isinstance(value, DomainName):
                str_values.append(value.string)
            elif isinstance(value, ipaddress.IPv4Address):
                str_values.append(value.exploded)
        return str(str_values).replace('\'', '')
    else:
        raise ValueError


def stamp_for_csv_row(rr: RRecord) -> List[str]:
    """
    Static method that returns a string representation divided in 3 elements of a list: name, type, values.

    :param rr: The resource record.
    :type rr: RRecord
    :return: String representation in a 3 elements list.
    :rtype: List[str]
    """
    lst = list()
    lst.append(rr.name)
    lst.append(rr.type.to_string())
    lst.append(stamp_values(rr.type, rr.values))
    return lst
