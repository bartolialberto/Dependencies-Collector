from typing import Set, Callable
from entities.enums.ResolvingErrorCauses import ResolvingErrorCauses


class UnresolvedEntityWrapper:
    """
    This class represents a 'container' that wraps an unresolved entity and the cause of why it happened in the form
    of a ResolvingErrorCauses enum. It is possible to populate another attribute to set even the input entity that
    produced such unresolved entity.

    ...

    Attributes
    ----------
    entity : any
        The unresolved entity.
    cause : ResolvingErrorCauses
        The cause of such missed resolution.
    entity_cause : any or None
        None or the input entity that caused the entity to be unresolved.
    """
    def __init__(self, entity: any, cause: ResolvingErrorCauses):
        """
        Initialize object. The entity cause is set to None.

        :param entity: The unresolved entity.
        :type entity: any
        :param cause: The cause of such missed resolution.
        :type cause: ResolvingErrorCauses
        """
        self.entity = entity
        self.cause = cause
        self.entity_cause = None

    def because_of(self, another_entity: any) -> None:
        """
        Method that sets the input entity that caused the entity to be unresolved.

        :param another_entity: The input entity that caused the entity to be unresolved.
        :type another_entity: any
        """
        self.entity_cause = another_entity

    @staticmethod
    def create_from_set(_set: set, cause: ResolvingErrorCauses) -> Set['UnresolvedEntityWrapper']:     # FORWARD DECLARATIONS (REFERENCES)
        """
        Static method that creates a set of UnresolvedEntityWrapper objects from another set of entities, and set every
        UnresolvedEntityWrapper cause attribute to the cause parameter.

        :param _set: A set of entities.
        :type _set: set
        :param cause: The cause to set all of the entities.
        :type cause: ResolvingErrorCauses
        :return: The resulting set of UnresolvedEntityWrapper
        :rtype: Set[UnresolvedEntityWrapper]
        """
        result = set()
        for elem in _set:
            result.add(UnresolvedEntityWrapper(elem, cause))
        return result
