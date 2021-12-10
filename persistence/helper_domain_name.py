from typing import List
from peewee import DoesNotExist
from entities.Zone import Zone
from persistence import helper_zone
from persistence.BaseModel import ZoneEntity, NameserverEntity, BelongsAssociation, DomainNameEntity, DependsAssociation


def multiple_inserts(result: dict) -> None:
    """
    This method executes multiple insert methods from the DNS resolving result (dictionary).

    :param result: The DNS resolving result.
    :type result: Dict[str, List[Zone]]
    """
    for domain_name in result.keys():
        for zone in result[domain_name]:
            insert(domain_name, zone)


def insert(domain_name: str, zone: Zone) -> None:
    """
    This method inserts in the database of the application (DB) all the zone dependencies associated with a domain name.
    This method doesn't need any data already persisted in the DB.

    :param domain_name: A domain name.
    :type domain_name: str
    :param zone: A zone object.
    :type zone: Zone
    """
    z, created = ZoneEntity.get_or_create(name=zone.name)
    for nameserver_rr in zone.nameservers:
        n, created = NameserverEntity.get_or_create(name=nameserver_rr.name, ip=nameserver_rr.get_first_value())
        BelongsAssociation.get_or_create(zone=z, nameserver=n)
    d, created = DomainNameEntity.get_or_create(name=domain_name)
    DependsAssociation.get_or_create(domain=d, zone=z)


def get_zone_dependencies(domain_name: str) -> List[Zone]:
    """
    Query that retrieves all the zone dependencies present in the database related with a domain name.

    :param domain_name: The domain name.
    :type domain_name: str
    :raise: If the corresponding entity of the domain name or a zone is not found.
    :return: All the Zone dependencies.
    :rtype: List[Zone]
    """
    try:
        DomainNameEntity.get(DomainNameEntity.name == domain_name)
    except DoesNotExist:
        raise
    zone_entities = list()
    zone_list = list()
    query = DependsAssociation.select()\
        .join_from(DependsAssociation, DomainNameEntity)\
        .join_from(DependsAssociation, ZoneEntity)\
        .where(DomainNameEntity.name == domain_name)
    for row in query:
        zone_entities.append(row.zone)
        try:
            z = helper_zone.get(row.zone.name)
        except DoesNotExist:
            raise
        zone_list.append(z)
    return zone_list



