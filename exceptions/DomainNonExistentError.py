class DomainNonExistentError(Exception):
    for_domain_name: str

    def __init__(self, domain_name: str):
        temp = f"Domain name: {domain_name} refers to a non-existent domain"
        self.message = temp
        self.for_domain_name = domain_name
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
