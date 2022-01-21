class TableNotPresentError(Exception):
    message: str
    for_as_number: str or int

    def __init__(self, param: int):
        temp = f"No table found in ROV page for AS number: {str(param)}."
        self.for_as_number = param
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
