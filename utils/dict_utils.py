def merge_current_dict_to_total(total_results_dict: dict, current_results_dict: dict) -> None:
    """
    This static method merges a dictionary into another dictionary.

    :param total_results_dict: The dictionary that takes the infos of the other one.
    :type total_results_dict: dict
    :param current_results_dict: The dictionary which all the infos are taken.
    :type current_results_dict: dict
    """
    for key in current_results_dict.keys():
        total_results_dict[key] = current_results_dict[key]


def merge_current_dict_with_set_values_to_total(total_results_dict: dict, current_results_dict: dict) -> None:
    """
    This static method merges a dictionary into another dictionary following the structure of the
    MultipleDnsZoneDependenciesResult dictionaries attributes, which means that values are set.

    :param total_results_dict: The dictionary that takes the infos of the other.
    :type total_results_dict: dict
    :param current_results_dict: The dictionary which all the infos are taken.
    :type current_results_dict: dict
    """
    for key in current_results_dict.keys():
        try:
            total_results_dict[key]
        except KeyError:
            total_results_dict[key] = set()
        finally:
            for elem in current_results_dict[key]:
                total_results_dict[key].add(elem)
