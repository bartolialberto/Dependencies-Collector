class PathNotFoundError(Exception):
    def __init__(self, name: str):
        temp = f"Path '{name}' not found."
        self.for_name = name
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
