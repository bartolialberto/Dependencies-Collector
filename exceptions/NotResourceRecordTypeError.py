class NotResourceRecordTypeError(Exception):
    def __init__(self, string: str):
        temp = f"'{string}' is not a valid resource record type."
        self.message = temp
        self.for_string = string
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
