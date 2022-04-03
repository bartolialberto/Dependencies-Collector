from ipaddress import IPv4Address
from typing import List
from entities.DomainName import DomainName
from entities.enums.TypesRR import TypesRR
from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError
from utils import resource_records_utils


class RRecord:
    """
    This class represent a simple resource record. Semantically it represents only the data structures, not the fact
    that is a real existent resource record.

    ...

    Attributes
    ----------
    name : DomainName
        The name field of the resource record.
    type : TypesRR
        The type field of the resource record.
    values : List[DomainName or ipaddress.IPv4Address]
        The values field of the resource record.
    """

    def __init__(self, name: DomainName or str, type_rr: TypesRR, values: List[str]):
        """
        Instantiate a RRecord object initializing all the attributes defined above.

        :param name: The name.
        :type name: DomainName or str
        :param type_rr: The type.
        :type type_rr: TypesRR
        :param values: The values.
        :type values: List[str]
        """
        if isinstance(name, str):
            self.name = DomainName(name)
        else:
            self.name = name
        self.type = type_rr
        self.values = RRecord.construct_objects(type_rr, values)

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
            if self.name == other.name and self.type == other.type:
                return True
            else:
                return False
        else:
            return False

    def get_first_value(self) -> DomainName or IPv4Address:
        """
        Gets the first value in the values field.

        :return: The first value.
        :rtype: DomainName or IPv4Address
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
        values = list()
        for val in split_values:
            values.append(val)
        return RRecord(DomainName(split_entry[0]), type_rr, values)

    def __str__(self):
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        return f"{self.name}\t{self.type.to_string()}\t{resource_records_utils.stamp_values(self.type, self.values)}"

    def __hash__(self) -> int:
        return hash((self.name, self.type))

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
        return split_value[1]       # TODO: se Ã¨ un IP? Da gestire

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
                result.append(RRecord(DomainName(prev_domain_name), TypesRR.CNAME, [domain_name]))
                prev_domain_name = domain_name

            return result

    @staticmethod
    def construct_objects(type_rr: TypesRR, values: List[str]) -> List[DomainName or IPv4Address]:
        if type_rr == TypesRR.A:
            obj_values = list()
            for value in values:
                if isinstance(value, IPv4Address):
                    obj_values.append(value)
                else:
                    try:
                        obj_values.append(IPv4Address(value))
                    except ValueError:
                        raise
            return obj_values
        elif type_rr == TypesRR.CNAME or type_rr == TypesRR.NS:
            domain_names = list()
            for value in values:
                if isinstance(value, DomainName):
                    domain_names.append(value)
                else:
                    domain_names.append(DomainName(value))
            return domain_names
        elif type_rr == TypesRR.MX:
            obj_values = list()
            for value in values:
                if isinstance(value, DomainName) or isinstance(value, IPv4Address):
                    obj_values.append(value)
                else:
                    split_string = value.split(' ')
                    split_value = split_string[-1]
                    try:
                        val = IPv4Address(split_value)
                    except ValueError:
                        val = DomainName(split_value)
                    obj_values.append(val)
            return obj_values
        else:
            raise ValueError
