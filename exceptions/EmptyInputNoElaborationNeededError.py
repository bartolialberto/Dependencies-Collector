class EmptyInputNoElaborationNeededError(Exception):
    message: str

    def __init__(self):
        temp = "No input for function so elaboration doesn't have to start."
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
