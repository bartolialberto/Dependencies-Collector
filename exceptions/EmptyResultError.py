class EmptyResultError(Exception):
    message: str

    def __init__(self):
        temp = "Empty result retrieved."
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
