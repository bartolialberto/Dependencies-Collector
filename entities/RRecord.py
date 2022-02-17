import ipaddress
from typing import List
from entities.enums.TypesRR import TypesRR
from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError
from utils import domain_name_utils


class RRecord:
    """
    This class represent a simple resource record. Semantically it represents only the data structures, not the fact
    that is a real existent resource record.

    ...

    Attributes
    ----------
    name : `str`
        The name field of the resource record.
    type : `TypesRR`
        The type field of the resource record.
    values : `List[str]`
        The values field of the resource record.
    """

    def __init__(self, name: str, type_rr: TypesRR, values: str or List[str]):
        """
        Instantiate a RRecord object initializing all the attributes defined above.

        :param name: The name.
        :type name: str
        :param type_rr: The type.
        :type type_rr: TypesRR
        :param values: The values.
        :type values: str or List[str]
        """
        self.name = name
        self.type = type_rr
        if isinstance(values, str):
            temp = list()
            temp.append(values)
            self.values = temp
        else:
            self.values = values

    def __eq__(self, other: any) -> bool:
        """
        This method returns True only if self and other are semantically equal.
        This equality depends upon the developer.

        :param other: Another RRecord object.
        :type other: RRecord
        :return: True or False if the 2 objects are equal.
        :rtype: bool
        """
        if isinstance(other, RRecord):
            if domain_name_utils.equals(self.name, other.name) and self.type == other.type:
                return True
            else:
                return False
        else:
            return False

    def get_first_value(self) -> str:
        """
        Gets the first value in the values field.

        :return: The first value.
        :rtype: str
        """
        return self.values[0]

    @staticmethod
    def parse_from_csv_entry_as_str(entry: str, separator=';') -> 'RRecord':     # FORWARD DECLARATIONS (REFERENCES)
        """
        A static method that takes a string which represents a resource record as described in this
        class.

        :param entry: The string.
        :type entry: str
        :param separator: The string character that separates columns (of an entry) in the string.
        :type separator: str
        :raise ValueError: If the string separated from the comma are least than 3.
        :raise NotResourceRecordTypeError: If the type associated with the type is not matchable with any type as
        described in class/enum TypesRR.
        :returns: The parsed RRecord object.
        :rtype: RRecord
        """
        temp = entry.replace("[", "")
        temp = temp.replace("]", "")
        temp = temp.replace("\n", "")
        split_entry = temp.split(separator)
        if len(split_entry) != 3:
            raise ValueError()
        try:
            type_rr = TypesRR.parse_from_string(split_entry[1])
        except NotResourceRecordTypeError:
            raise
        # parsing values
        split_values = split_entry[2].split(',')
        values = []
        for val in split_values:
            values.append(val)
        return RRecord(split_entry[0], type_rr, values)

    def __str__(self):
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        return f"{self.name}\t{self.type.to_string()}\t{str(self.values)}"

    @staticmethod
    def parse_mail_server_from_value(value: str) -> str:
        """
        This static method parse the mail server from the value string belonging in the values field of a RR.

        :param value: A string.
        :type value: str
        :return: The mail server parsed.
        :rtype: str
        """
        split_value = value.split(' ')
        return split_value[1]       # TODO: se è un IP? Da gestire

    @staticmethod
    def construct_cname_rrs_from_list_access_path(domain_names: List[str]) -> List['RRecord']:      # FORWARD DECLARATIONS (REFERENCES)
        """
        This method takes a list of strings that should represents an access path or a name resolution path, and returns
        such list as a path of CNAME RRs.

        :param domain_names: An access path or name resolution path of domain names.
        :type domain_names: List[str]
        :return: A list of CNAME RRs.
        :rtype: List[RRecord]
        """
        if len(domain_names) == 0:
            raise ValueError
        elif len(domain_names) == 1:
            raise ValueError
        else:
            result = list()
            prev_domain_name = domain_names[0]
            for domain_name in domain_names[1:]:
                result.append(RRecord(prev_domain_name, TypesRR.CNAME, domain_name))
                prev_domain_name = domain_name
            return result

    @staticmethod
    def standardize_rr_domain_names(rr: 'RRecord') -> 'RRecord':
        # TODO: docs
        standardized_name = domain_name_utils.standardize_for_application(rr.name)
        if rr.type != TypesRR.A:
            if rr.type == TypesRR.MX:
                standardized_values = list()
                for val in rr.values:
                    split_val = val.split(' ')
                    if ipaddress.IPv4Address(split_val[-1]):
                        standardized_values.append(val)
                    else:
                        standardized_values.append(split_val[0]+' '+domain_name_utils.standardize_for_application(split_val[-1]))
            else:
                standardized_values = list()
                for val in rr.values:
                    standardized_values.append(domain_name_utils.standardize_for_application(val))
        else:
            standardized_values = rr.values
        return RRecord(standardized_name, rr.type, standardized_values)

    @staticmethod
    def standardize_multiple_rr(rrs: List['RRecord']) -> List['RRecord']:
        # TODO: docs
        standardized_rrs = list()
        for rr in rrs:
            standardized_rrs.append(RRecord.standardize_rr_domain_names(rr))
        return standardized_rrs
