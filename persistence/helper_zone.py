from peewee import DoesNotExist
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from entities.Zone import Zone
from persistence.BaseModel import ZoneEntity, NameserverEntity, BelongsAssociation


def get(zone_name: str) -> Zone:
    """
    Query that retrieves the Zone object result presents in the database defined by the zone name parameter.

    :param zone_name: The zone name.
    :type zone_name: str
    :return: The Zone object result from the query.
    :rtype: Zone
    """
    try:
        ze = ZoneEntity.get(ZoneEntity.name == zone_name)
    except DoesNotExist:
        raise
    nameservers = list()
    query = NameserverEntity.select().join(BelongsAssociation).where(BelongsAssociation.zone_id == ze.id)
    for r in query:
        nameservers.append(RRecord(r.name, TypesRR.A, r.ip))
        # TODO: aliases
    return Zone(zone_name, nameservers, [])

