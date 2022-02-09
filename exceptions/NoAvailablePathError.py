class NoAvailablePathError(Exception):
    for_param: str

    def __init__(self, param: str):
        temp = f"No alias path found for: {param}"
        self.message = temp
        self.for_param = param
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
