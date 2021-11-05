class UnknownReasonError(Exception):
    def __init__(self, message="An error occurred."):
        self.message = message

    def __str__(self):
        return f'{self.message}'
