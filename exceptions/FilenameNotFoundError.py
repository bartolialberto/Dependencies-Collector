class FilenameNotFoundError(Exception):
    message: str
    for_filename: str

    def __init__(self, filename: str, path: str):
        temp = f"File with filename '{filename}' not found in path '{path}'."
        self.for_filename = filename
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
