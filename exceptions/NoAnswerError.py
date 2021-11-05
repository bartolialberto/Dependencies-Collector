from entities.TypesRR import TypesRR


class NoAnswerError(Exception):
    for_domain_name: str
    for_type: TypesRR

    def __init__(self, domain_name: str, _type: TypesRR):
        tmp = f"No answer for {_type.value} query of domain name '{domain_name}'."
        self.message = tmp
        self.for_domain_name = domain_name
        self.for_type = _type
        BaseException.__init__(self, tmp)

    def __str__(self):
        return f'{self.message}'
