class NotWantedTLDError(Exception):
    message: str

    def __init__(self):
        temp = "Resolved a domain name that is a TLD."
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
