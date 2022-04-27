class MainFrameScript:
    """
    This class represents a very simple container that contains infos representating a script and its withdraw.

    ...

    Attributes
    ----------
    src : str
        The src attribute value of the script HTML element.
    integrity : str or None
        The integrity attribute value of the script HTML. None is for absence.
    """
    def __init__(self, src: str, integrity: str or None):
        """
        Instantiate the object.

        :param src: The src attribute.
        :type src: str
        :param integrity: The integrity attribute.
        :type integrity: Optional[str]
        """
        self.src = src
        self.integrity = integrity

    def __eq__(self, other):
        """
        This method returns a boolean for comparing 2 objects equality.

        :param other:
        :return: The result of the comparison.
        :rtype: bool
        """
        if isinstance(other, MainFrameScript):
            if self.src == other.src:
                return True
            else:
                return False
        else:
            return False

    def __str__(self) -> str:
        """
        This method returns a human-readable string representation of this object.

        :return: A human-readable string representation of this object.
        :rtype: str
        """
        return f"MainPageScript: src={self.src}, integrity={self.integrity}"

    def __hash__(self) -> int:
        """
        This method returns the hash of this object. Should be defined alongside the __eq__ method with the same
        returning value from 2 objects.

        :return: Hash of this object.
        :rtype: int
        """
        return hash(self.src)
