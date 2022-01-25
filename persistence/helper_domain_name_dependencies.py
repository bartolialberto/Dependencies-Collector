from persistence.BaseModel import DomainNameEntity, ZoneEntity, DomainNameDependenciesAssociation


def insert(dne: DomainNameEntity, ze: ZoneEntity) -> DomainNameDependenciesAssociation:
    nda, created = DomainNameDependenciesAssociation.get_or_create(domain_name=dne, zone=ze)
    return nda
