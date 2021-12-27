from entities import TypesRR


class NoRecordInCacheError(Exception):
    for_domain_name: str
    for_type: TypesRR

    def __init__(self, domain_name: str, _type: TypesRR):
        temp = f"No record found in cache for name:'{domain_name}' and type: '{_type.url}'"
        self.message = temp
        self.for_domain_name = domain_name
        self.for_type = _type
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
