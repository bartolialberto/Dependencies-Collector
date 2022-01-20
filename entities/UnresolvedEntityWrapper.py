from typing import Set, Callable
from entities.enums.ResolvingErrorCauses import ResolvingErrorCauses


class UnresolvedEntityWrapper:
    # TODO
    def __init__(self, entity: any, cause: ResolvingErrorCauses):
        self.entity = entity
        self.cause = cause
        self.entity_cause = None

    def because_of(self, another_entity: any) -> None:
        self.entity_cause = another_entity

    @staticmethod
    def create_from_set(_set: set, cause: ResolvingErrorCauses) -> Set['UnresolvedEntityWrapper']:     # FORWARD DECLARATIONS (REFERENCES)
        result = set()
        for elem in _set:
            result.add(UnresolvedEntityWrapper(elem, cause))
        return result

    @staticmethod
    def create_from_set_with_function_for_entity_cause(_set: set, cause: ResolvingErrorCauses, func: Callable) -> Set['UnresolvedEntityWrapper']:     # FORWARD DECLARATIONS (REFERENCES)
        result = set()
        for elem in _set:
            tmp = UnresolvedEntityWrapper(elem, cause)
            tmp.because_of(func(elem))
            result.add(tmp)
        return result
