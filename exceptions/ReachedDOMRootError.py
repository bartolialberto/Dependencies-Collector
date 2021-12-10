class ReachedDOMRootError(Exception):
    message: str

    def __init__(self):
        temp = "Reached DOM root."
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
