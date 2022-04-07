from peewee import DoesNotExist
from entities.DomainName import DomainName
from persistence import helper_domain_name
from persistence.BaseModel import ZoneEntity, DomainNameEntity, AliasToZoneAssociation


def insert(ze: ZoneEntity, dne: DomainNameEntity) -> AliasToZoneAssociation:
    znafa, created = AliasToZoneAssociation.get_or_create(zone=ze, domain_name=dne)
    return znafa


def get_from_entity_domain_name(dne: DomainNameEntity) -> AliasToZoneAssociation:
    try:
        znaa = AliasToZoneAssociation.get(AliasToZoneAssociation.domain_name == dne)
    except DoesNotExist:
        raise
    return znaa


def get_from_domain_name(domain_name: DomainName) -> AliasToZoneAssociation:
    try:
        dne = helper_domain_name.get(domain_name)
    except DoesNotExist:
        raise
    return get_from_entity_domain_name(dne)
