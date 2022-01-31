from persistence.BaseModel import ZoneEntity, ZoneLinksAssociation


def insert(ze: ZoneEntity, ze_dep: ZoneEntity) -> ZoneLinksAssociation:
    zla, created = ZoneLinksAssociation.get_or_create(zone=ze, dependency=ze_dep)
    return zla
