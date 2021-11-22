# coding=utf-8
import dns.resolver

res = dns.resolver.Resolver()
res.nameservers = ["1.1.1.1"]
"""
This module contains the class RRecord.
"""

class RRecord:
    """
    RRecord encapsulate a dns resource record.

    """
    name = ""
    type = None
    values = None
#qui è per ora gestito il caso ottimale ma va cambiato es se metto name che non è di un server torno errore, non Ip inesistente
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


def findRRecord(nam, ty):
    """
    This method is a static method. It resolves a dns query with the name and type, which are strings passed as input.
    :param nam: a string representing the name of a dns query.
    :param ty: a string representing the type of a dn query
    :return: a dictionary with two keys. The first key is “Result” and its value is an object of this same class with name, type and the value from the response of the dns query. If the query fails because there is no answer this method returns the string “NoAnswer” as value of the dns query, if name is a domain that does not exist this method returns the string “NXDomain” as value of the dns query, if the query fails because of another reason this method returns None. The second key is “CNAME” and its value is a list of objects of this same class with type CNAME, it is the list of CNAME records the dns query has to do to find the response to the query made with name and type passed as input. If there are no CNAME query to be done to resolve the dns query, the value of this key is None.
    """
    #return a dict con CNAME che è false se non c'è o se è NXDomain o NOanswer e in Result c'è la risposta, eventualmente con NXDomain o Noanswer
    #return a list of rrecord, in the case it follow a chain o CNAMES rrecord
    rrecords = list()
    returnValue = {
        "Result" : None,
        "CNAME" : None
    }
    try:
        result = res.resolve(nam, ty)
        for cnm in result.chaining_result.cnames:
            splitted = cnm.to_text().split()
            tmp = list()
            tmp.append(splitted[4])
            rrecords.append(RRecord(splitted[0], splitted[3], tmp))
        if len(rrecords) == 0:
            pass
        else:
            returnValue["CNAME"] = rrecords
        responseList = list()
        for ad in result:
            responseList.append(ad.to_text())
        returnValue["Result"] = RRecord(result.canonical_name.to_text(), ty, responseList)
        return returnValue

    except dns.resolver.NXDOMAIN:
        returnValue["Result"] = RRecord(nam, ty, "NXDomain")
        return returnValue
    except dns.resolver.NoAnswer:
        returnValue["Result"] = RRecord(nam, ty, "NoAnswer")
        return returnValue
    except Exception as e:
        print("Unexpected error on findRRecord ", e)
        return None
