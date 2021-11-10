from typing import List
from entities.TypesRR import TypesRR
from exceptions.NotResourceRecordTypeError import NotResourceRecordTypeError


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
    values : `list[str]`
        The values field of the resource record.
    """
    name: str
    type: TypesRR
    values: List[str]

    def __init__(self, name: str, type_rr: TypesRR, values: str or List[str]):
        """
        Instantiate a RRecord object initializing all the attributes defined above.

        Parameters
        ----------
        name : `str`
            The name.
        type_rr : `TypesRR`
            The type.
        values : `str` of 'List[tr]`
            The values.
        """
        self.name = name
        self.type = type_rr
        if isinstance(values, str):
            temp = list()
            temp.append(values)
            self.values = temp
        else:
            self.values = values

    def __eq__(self, other):
        if isinstance(other, RRecord):
            if self.name == other.name and self.type is other.type:
                return True
            else:
                return False
        else:
            return False

    def get_first_value(self) -> str:
        return self.values[0]

    @staticmethod
    def parse_from_csv_entry_as_str(entry: str) -> 'RRecord':     # FORWARD DECLARATIONS (REFERENCES)
        """
        A static method that takes a string comma-separated which represents a resource record as described in this
        class.

        Parameters
        ----------
        entry : `str`
            The string.

        Returns
        -------
        rr : `RRecord`
            The parsed RRecord object.

        Raises
        ------
        ValueError
            If the string separated from the comma are least than 3.
        NotResourceRecordTypeError
            If the type associated with the type is not matchable with any type as described in class/enum TypesRR.
        """
        temp = entry.replace("[", "")
        temp = temp.replace("]", "")
        temp = temp.replace('"', "")  # TODO: risolvere questo problema
        temp = temp.replace("\n", "")
        split_entry = temp.split(",")
        if len(split_entry) < 3:
            raise ValueError()
        try:
            type_rr = TypesRR.parse_from_string(split_entry[1])
        except NotResourceRecordTypeError:
            raise
        # parsing values
        values = []
        for val in split_entry[2:]:
            values.append(val)
        return RRecord(split_entry[0], type_rr, values)
