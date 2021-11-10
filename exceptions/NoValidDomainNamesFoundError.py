class NoValidDomainNamesFoundError(Exception):
    filepath: str

    def __init__(self, filepath: str):
        temp = f"No valid domain names found in file {filepath}."
        self.for_filepath = filepath
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'