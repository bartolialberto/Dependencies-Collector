from persistence.BaseModel import DomainNameEntity, ZoneEntity, NameDependenciesAssociation


def insert(dne: DomainNameEntity, ze: ZoneEntity) -> NameDependenciesAssociation:
    nda, created = NameDependenciesAssociation.get_or_create(domain_name=dne, zone=ze)
    return nda
