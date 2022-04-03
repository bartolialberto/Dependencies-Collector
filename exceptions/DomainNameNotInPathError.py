from entities.DomainName import DomainName


class DomainNameNotInPathError(Exception):
    message: str
    for_param: DomainName

    def __init__(self, domain_name: DomainName):
        temp = f"Domain name {str(domain_name)} is not in path."
        self.for_param = domain_name
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
