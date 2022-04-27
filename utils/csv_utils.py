import csv
from csv import Dialect


def return_personalized_dialect(separator=";") -> Dialect:
    """
    Static method that returns the personalized dialect related to CSV file format used in this project. If not present
    it is registered in the module csv.

    :param separator: Separator string used.
    :type separator: str
    :return: Personalized dialect used in this project.
    :rtype: Dialect
    """
    try:
        result = csv.get_dialect('personalized')
        return result
    except csv.Error:
        csv.register_dialect('personalized', escapechar='\\', delimiter=f'{separator}', quoting=csv.QUOTE_NONE)
        return csv.get_dialect('personalized')


def return_personalized_dialect_name(separator=";") -> str:
    """
    Static method that returns the personalized dialect name related to CSV file format used in this project. If not
    present it is registered in the module csv.

    :param separator: Separator string used.
    :type separator: str
    :return: Personalized dialect name used in this project.
    :rtype: str
    """
    try:
        result = csv.get_dialect('personalized')
        return 'personalized'
    except csv.Error:
        csv.register_dialect('personalized', escapechar='\\', delimiter=f'{separator}', quoting=csv.QUOTE_NONE)
        return 'personalized'
