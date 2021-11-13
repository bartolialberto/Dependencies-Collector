import csv


def return_personalized_dialect(separator=";"):
    try:
        result = csv.get_dialect('personalized')
        return result
    except csv.Error:
        csv.register_dialect('personalized', escapechar='\\', delimiter=f'{separator}', quoting=csv.QUOTE_NONE)
        return csv.get_dialect('personalized')


def return_personalized_dialect_name(separator=";"):
    try:
        result = csv.get_dialect('personalized')
        return 'personalized'
    except csv.Error:
        csv.register_dialect('personalized', escapechar='\\', delimiter=f'{separator}', quoting=csv.QUOTE_NONE)
        return 'personalized'
