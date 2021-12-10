class ErrorLog:
    """
    This class represents a very simple error log object for the usage needed in this application.

    ...

    Attributes
    ----------
    error_type : str
        The name of the error.
    entity_cause : str
        A string representation of the entity that caused the problem.
    reason_phrase : str
        A brief string description of the problem.
    """
    def __init__(self, exception: BaseException, entity_cause: str, reason_phrase: str):
        """
        Initialize the object.

        :param exception: The error raised.
        :type exception: BaseException
        :param entity_cause: The string representation of the entity that caused the problem.
        :type entity_cause: str
        :param reason_phrase: The reason phrase.
        :type reason_phrase: str
        """
        self.error_type = type(exception).__name__      # takes the name of the error
        self.entity_cause = entity_cause
        self.reason_phrase = reason_phrase

    def __str__(self) -> str:
        return f"{self.error_type}\t{self.entity_cause}\t{self.reason_phrase}"

    def __eq__(self, other) -> bool:
        if isinstance(other, ErrorLog):
            return self.error_type == other.error_type and self.entity_cause == other.entity_cause
        else:
            return False
