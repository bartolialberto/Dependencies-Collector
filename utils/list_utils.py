from entities.RRecord import RRecord
from entities.TypesRR import TypesRR


def append_to_list_with_no_duplicates(_list: list, element):
    if element not in _list:
        _list.append(element)


def remove_duplicates_from_list(_list: list):
    return list(dict.fromkeys(_list))


def remove_none_elements_from_list(_list: list):
    return list(filter(lambda e: e is not None, _list))


def is_list_of_type(_list: list, _class):       # Zones.RRecord
    for element in _list:
        if isinstance(element, _class):
            pass
        else:
            return False
    return True


def is_list_of_type_RRecord_and_rr_type(_list: list, _type: TypesRR):
        for element in _list:
            if isinstance(element, RRecord) and (element.type is _type):
                pass
            else:
                return False
        return True
