from peewee import DoesNotExist
from persistence.BaseModel import ZoneEntity, DomainNameEntity, AliasToZoneAssociation


def insert(ze: ZoneEntity, dne: DomainNameEntity) -> AliasToZoneAssociation:
    znafa, created = AliasToZoneAssociation.get_or_create(zone=ze, domain_name=dne)
    return znafa


def get_from_entity_zone_name(ze: ZoneEntity) -> AliasToZoneAssociation:
    try:
        znaa = AliasToZoneAssociation.get(AliasToZoneAssociation.zone == ze)
    except DoesNotExist:
        raise
    return znaa


def get_from_entity_domain_name(dne: DomainNameEntity) -> AliasToZoneAssociation:
    try:
        znaa = AliasToZoneAssociation.get(AliasToZoneAssociation.domain_name == dne)
    except DoesNotExist:
        raise
    return znaa
