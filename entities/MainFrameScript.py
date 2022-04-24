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
        self.src = src
        self.integrity = integrity

    def __eq__(self, other):
        if isinstance(other, MainFrameScript):
            if self.src == other.src:
                return True
            else:
                return False
        else:
            return False

    def __str__(self) -> str:
        """
        This method returns a string representation of this object.

        :return: A string representation of this object.
        :rtype: str
        """
        return f"MainPageScript: src={self.src}, integrity={self.integrity}"

    def __hash__(self) -> int:
        return hash(self.src)
