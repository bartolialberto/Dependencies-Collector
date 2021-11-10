class FileWithExtensionNotFoundError(Exception):
    message: str
    for_extension: str

    def __init__(self, extension: str, path: str):
        temp = f"File with extension '{extension}' not found in path '{path}'."
        self.for_extension = extension
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
