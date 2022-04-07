import ipaddress
from entities.DomainName import DomainName
from entities.enums.TypesRR import TypesRR


def stamp_values(type_rr: TypesRR, values: list) -> str:
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
