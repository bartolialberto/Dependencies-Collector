from entities.DomainName import DomainName


class PathIntegrityError(Exception):
    message: str
    for_param: DomainName

    def __init__(self):
        temp = f"Path data integrity through chain is violated."
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
