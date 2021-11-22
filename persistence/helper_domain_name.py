from typing import List

from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from entities.Zone import Zone
from persistence.BaseModel import NameserverEntity, ZoneEntity, DomainNameEntity, DependsAssociation, BelongsAssociation


def multiple_inserts(result_dict: dict):
    for domain_name in result_dict.keys():
        for zone in result_dict[domain_name]:
            insert(domain_name, zone)


def insert(domain_name: str, zone: Zone):
    z, created = ZoneEntity.get_or_create(name=zone.name)        # z: Tuple[Model, bool]
    for nameserver_rr in zone.nameservers:
        n, created = NameserverEntity.get_or_create(name=nameserver_rr.name, ip=nameserver_rr.get_first_value())
        BelongsAssociation.get_or_create(zone=z, nameserver=n)
    d, created = DomainNameEntity.get_or_create(name=domain_name)
    DependsAssociation.get_or_create(domain=d, zone=z)


def get_zone_dependencies(domain_name: str) -> List[Zone]:
    query = DependsAssociation.select()\
        .join_from(DependsAssociation, DomainNameEntity)\
        .join_from(DependsAssociation, ZoneEntity)\
        .where(DomainNameEntity.name == domain_name)
    zone_entities = list()
    for row in query:
        zone_entities.append(row.zone)
    zone_list = list()
    for zone_entity in zone_entities:
        query = BelongsAssociation.select()\
            .join_from(BelongsAssociation, ZoneEntity)\
            .join_from(BelongsAssociation, NameserverEntity)\
            .where(ZoneEntity.id == zone_entity.id)
        nameserver_entities = list()
        for row in query:
            nameserver_entities.append(row.nameserver)
        nameserver_list = list()
        for nameserver_entity in nameserver_entities:
            nameserver_list.append(RRecord(nameserver_entity.name, TypesRR.A, nameserver_entity.ip))
        zone_list.append(Zone(zone_entity.name, nameserver_list, list()))
    return zone_list








def test(domain_name: str) -> List[Zone]:
    query = DependsAssociation.select().join(DomainNameEntity).where(DomainNameEntity.name == domain_name)
    zone_entities = list()
    for row in query:
        zone_entity = ZoneEntity.get_by_id(row.zone_id)
        zone_entities.append(zone_entity)
    for zone_entity in zone_entities:
        query = BelongsAssociation.select().join(ZoneEntity).where(ZoneEntity.id == zone_entity.id)
        nameserver_entities = list()
        for row in query:
            nameserver_entity = NameserverEntity.get_by_id(row.nameserver_id)
            nameserver_entities.append(nameserver_entity)
    print(zone_entities)



