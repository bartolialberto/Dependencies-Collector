from persistence.BaseModel import ZoneEntity, NameServerEntity, ZoneComposedAssociation


def insert(ze: ZoneEntity, nse: NameServerEntity) -> ZoneComposedAssociation:
    zca, created = ZoneComposedAssociation.get_or_create(zone=ze, name_server=nse)
    return zca
