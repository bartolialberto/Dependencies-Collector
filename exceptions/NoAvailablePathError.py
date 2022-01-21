class NoAvailablePathError(Exception):
    for_domain_name: str

    def __init__(self, domain_name: str):
        temp = f"No alias path found for name: {domain_name}"
        self.message = temp
        self.for_domain_name = domain_name
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
