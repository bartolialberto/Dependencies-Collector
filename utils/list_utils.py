from entities.RRecord import RRecord
from entities.TypesRR import TypesRR


def append_with_no_duplicates(_list: list, element):
    if element not in _list:
        _list.append(element)


def update_element(_list: list, element_to_be_removed, new_element):
    _list.remove(element_to_be_removed)
    _list.append(new_element)


def remove_duplicates(_list: list):
    return list(dict.fromkeys(_list))


def remove_none_elements(_list: list):
    return list(filter(lambda e: e is not None, _list))


def are_all_objects_of_type(_list: list, _class):       # Zones.RRecord
    for element in _list:
        if isinstance(element, _class):
            pass
        else:
            return False
    return True


def are_all_objects_RRecord_and_rr_type(_list: list, rr_type: TypesRR):
    for element in _list:
        if isinstance(element, RRecord) and (element.type is rr_type):
            pass
        else:
            return False
    return True
