from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR


def append_with_no_duplicates(_list: list, element) -> None:
    """
    Appends an element to the parameter list only if the element is not already contained in the list parameter.

    :param _list: A list.
    :type _list: list
    :param element: An object.
    :type element: Any
    """
    if element not in _list:
        _list.append(element)


def update_element(_list: list, element_to_be_removed, new_element):
    """
    Remove an element and append the other.
    
    :param _list: 
    :type _list: list
    :param element_to_be_removed:
    :type element_to_be_removed: Any 
    :param new_element: 
    :type new_element: Any
    """
    _list.remove(element_to_be_removed)
    _list.append(new_element)


def remove_duplicates(_list: list):
    """
    Remove duplicates from list.

    :param _list: A list.
    :type _list: list
    """
    return list(dict.fromkeys(_list))


def remove_none_elements(_list: list):
    """
    Remove None elements from list.

    :param _list: A list.
    :type _list: list
    """
    return list(filter(lambda e: e is not None, _list))


def are_all_objects_of_type(_list: list, _class):       # Zones.RRecord
    """
    Control if all elements in the list are instance of a certain class.

    :param _list: A list.
    :type _list: list
    :param _class: A class type.
    :type _class: Any
    :return: True or False.
    :rtype: bool
    """
    for element in _list:
        if isinstance(element, _class):
            pass
        else:
            return False
    return True


def are_all_objects_RRecord_of_type(_list: list, rr_type: TypesRR):
    """
    A particular static method that control if a list has all elements of type RRecord and a certain attribute type.

    :param _list: A list.
    :type _list: list
    :param rr_type: The type of the RRecord object.
    :type rr_type: TypesRR
    :return: True or False.
    :rtype: bool
    """
    for element in _list:
        if isinstance(element, RRecord) and (element.type is rr_type):
            pass
        else:
            return False
    return True
