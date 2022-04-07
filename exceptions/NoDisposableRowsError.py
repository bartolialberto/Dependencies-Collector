class NoDisposableRowsError(Exception):
    message: str

    def __init__(self):
        temp = f"No disposable rows for query."
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
