from peewee import DoesNotExist
from persistence.BaseModel import ZoneEntity, DomainNameEntity, ZoneNameAliasAssociation


def insert(ze: ZoneEntity, dne: DomainNameEntity) -> ZoneNameAliasAssociation:
    znafa, created = ZoneNameAliasAssociation.get_or_create(zone=ze, domain_name=dne)
    return znafa


def get_from_entity_zone_name(ze: ZoneEntity) -> ZoneNameAliasAssociation:
    try:
        znaa = ZoneNameAliasAssociation.get(ZoneNameAliasAssociation.zone == ze)
    except DoesNotExist:
        raise
    return znaa


def get_from_entity_domain_name(dne: DomainNameEntity) -> ZoneNameAliasAssociation:
    try:
        znaa = ZoneNameAliasAssociation.get(ZoneNameAliasAssociation.domain_name == dne)
    except DoesNotExist:
        raise
    return znaa
