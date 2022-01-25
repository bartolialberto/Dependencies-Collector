from persistence.BaseModel import DirectZoneAssociation, DomainNameEntity, ZoneEntity


def insert(dne: DomainNameEntity, ze: ZoneEntity) -> DirectZoneAssociation:
    dza, created = DirectZoneAssociation.get_or_create(domain_name=dne, zone=ze)
    return dza
