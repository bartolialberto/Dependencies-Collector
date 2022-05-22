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


def remove_duplicates(_list: list):
    """
    Remove duplicates from list.

    :param _list: A list.
    :type _list: list
    """
    return list(dict.fromkeys(_list))


def merge_set_in_list(_list: list, _set: set, duplicates=False) -> list:
    for elem in _set:
        if duplicates:
            _list.append(elem)
        else:
            append_with_no_duplicates(_list, elem)
    return _list
