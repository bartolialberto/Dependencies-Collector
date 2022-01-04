from persistence.BaseModel import ZoneEntity, NameserverEntity, ZoneComposedAssociation


def insert(ze: ZoneEntity, nse: NameserverEntity) -> ZoneComposedAssociation:
    zca, created = ZoneComposedAssociation.get_or_create(zone=ze, nameserver=nse)
    return zca
