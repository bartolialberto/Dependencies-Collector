# coding=utf-8
import dns.resolver
from exceptions.UnknownReasonError import UnknownReasonError

resolver = dns.resolver.Resolver()
resolver.nameservers = ["1.1.1.1"]
"""
This module contains the class RRecord.
"""


class RRecord:
    """
    RRecord encapsulate a dns resource record.

    """
    name = ""       # string
    type = None     # string
    values = None   # list of strings

    # qui è per ora gestito il caso ottimale ma va cambiato es se metto name che non è di un server torno errore,
    # non Ip inesistente
    def __init__(self, nam, ty, value):
        """
        This class represents a dns resource record. name, type and value corresponds to the parts the resource record is composed of. name and type are strings, while value is a list of strings. This constructor initializes these class fields.
        :param nam: is a string representing the name of the resource record.
        :param ty: is a string representing the type of the resource record.
        :param value: represents the values in the dns response when it is queried with name and type in the corresponding fields. It is a list of strings.
        """
        self.name = nam
        self.type = ty
        self.values = value

    @staticmethod
    def find_resource_records(nam, ty):
        """
        This method is a static method. It resolves a dns query with the name and type (strings), passed as input.
        :param nam: a string representing the name of a dns query.
        :param ty: a string representing the type of a dn query
        :return: a dictionary with two keys. The first key is “Result” and its value is an object of this same class
        with name, type and the value from the response of the dns query. If the query fails because there is no answer
        this method returns the string “NoAnswer” as value of the dns query,
        if name is a domain that does not exist this method returns the string “NXDomain” as value of the dns query,
        if the query fails because of another reason this method returns None.
        The second key is “CNAME” and its value is a list of objects of this same class with type CNAME,
        it is the list of CNAME records the dns query has to do to find the response to the query made with
        name and type passed as input.
        If there are no CNAME query to be done to resolve the dns query, the value of this key is None.
        """
        cname_rrecords = list()
        try:
            answer = resolver.resolve(nam, ty)
            for cname in answer.chaining_result.cnames:
                temp = []
                for key in cname.items.keys():
                    temp.append(key.target)
                cname_rrecords.append(RRecord(cname.name, dns.rdatatype.to_text(cname.rdtype), temp))
            if len(cname_rrecords) == 0:    # no aliases found
                pass
            rrecords = list()
            for ad in answer:
                rrecords.append(ad.to_text())
            response_rrecords = RRecord(answer.canonical_name.to_text(), ty, rrecords)
            # risultato: tupla con:
            #       - RRecord di tipo ty con il risultato della query come campo RRecord.values
            #       - lista di RRecord per gli aliases attraversati per avere la risposta
            return response_rrecords, cname_rrecords
        except dns.resolver.NXDOMAIN:   # name is a domain that does not exist
            raise
        except dns.resolver.NoAnswer:   # there is no answer
            raise
        except Exception:   # fail because of another reason...
            raise UnknownReasonError()
