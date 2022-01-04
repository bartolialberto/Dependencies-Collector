from peewee import DoesNotExist
from entities.Zone import Zone
from persistence import helper_nameserver, helper_ip_address, helper_zone_composed, helper_access, helper_alias, \
    helper_domain_name
from persistence.BaseModel import ZoneEntity


def insert(name: str) -> ZoneEntity:
    ze, created = ZoneEntity.get_or_create(name=name)
    return ze


def insert_zone_object(zone: Zone):
    ze, created = ZoneEntity.get_or_create(name=zone.name)
    if created:
        pass
    else:
        return ze       # scorciatoia?

    for rr_nameserver in zone.nameservers:
        nse, nsdne = helper_nameserver.insert(rr_nameserver.name)
        helper_zone_composed.insert(ze, nse)
        iae = helper_ip_address.insert(rr_nameserver.get_first_value())
        helper_access.insert(nsdne, iae)

    for rr_alias in zone.aliases:
        # get???
        # ne = helper_domain_name.insert(rr_alias.name)
        dne, ne = helper_nameserver.insert(rr_alias.name)
        for alias in rr_alias.values:
            ane = helper_domain_name.insert(alias)
            helper_alias.insert(ne, ane)

    return ze


def get(zone_name: str) -> ZoneEntity:
    try:
        ze = ZoneEntity.get_by_id(zone_name)
    except DoesNotExist:
        raise
    return ze
