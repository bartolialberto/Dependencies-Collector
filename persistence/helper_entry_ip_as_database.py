from peewee import DoesNotExist
from entities.IpAsDatabase import EntryIpAsDatabase
from persistence import helper_range, helper_belonging_network, helper_matches, helper_ip_network
from persistence.BaseModel import NameserverEntity, EntryIpAsDatabaseEntity, MatchesAssociation, IpRangeEntity, \
    IpNetworkEntity, BelongingNetworkAssociation, HasAssociation


def multiple_inserts(results: dict, persist_errors: bool) -> None:
    for nameserver in results.keys():
        ip_string = results[nameserver][0]
        entry = results[nameserver][1]
        belonging_network = results[nameserver][2]
        #
        try:
            nse = NameserverEntity.get(NameserverEntity.name == nameserver)
        except DoesNotExist:
            raise
        if entry is None and belonging_network is None:
            if persist_errors:
                try:
                    helper_matches.temp_insert_entry_ip_as_db(nse, None)
                except DoesNotExist:
                    raise
            else:
                pass
        elif belonging_network is None:
            ee, created = EntryIpAsDatabaseEntity.get_or_create(autonomous_system_number=entry.as_number, country_code=entry.country_code, autonomous_system_description=entry.as_description)
            re, he = helper_range.insert_with_relation_too(ee, entry.start_ip_range, entry.end_ip_range)
            try:
                helper_matches.temp_insert_entry_ip_as_db(nse, ee)
            except DoesNotExist:
                raise
            if persist_errors:
                bne = helper_belonging_network.insert(ee, None)
            else:
                pass
        else:
            ee, created = EntryIpAsDatabaseEntity.get_or_create(autonomous_system_number=entry.as_number, country_code=entry.country_code, autonomous_system_description=entry.as_description)
            re, he = helper_range.insert_with_relation_too(ee, entry.start_ip_range, entry.end_ip_range)
            ine, bna = helper_ip_network.insert_with_ip_as_relation_too(belonging_network, ee)
            try:
                helper_matches.temp_insert_entry_ip_as_db(nse, ee)
            except DoesNotExist:
                raise


def insert(entry: EntryIpAsDatabase) -> EntryIpAsDatabaseEntity:
    ee, created = EntryIpAsDatabaseEntity.get_or_create(autonomous_system_number=entry.as_number, country_code=entry.country_code, autonomous_system_description=entry.as_description)
    return ee


def get_from_nameserver(nameserver: str) -> EntryIpAsDatabaseEntity:
    try:
        nse = NameserverEntity.get(NameserverEntity.name == nameserver)
    except DoesNotExist:
        raise
    try:
        ma = MatchesAssociation.get(MatchesAssociation.entry_ip_as_database_id == nse.id)
    except DoesNotExist:
        raise
    try:
        ee = EntryIpAsDatabaseEntity.get_by_id(ma.entry_ip_as_database_id)
    except DoesNotExist:
        raise
    return ee


def get_with_relation_too_from_nameserver(nameserver: str) -> (EntryIpAsDatabaseEntity, IpRangeEntity, IpNetworkEntity):
    try:
        ee = get_from_nameserver(nameserver)
    except DoesNotExist:
        raise
    query = BelongingNetworkAssociation.select()\
        .join_from(BelongingNetworkAssociation, EntryIpAsDatabaseEntity)\
        .join_from(BelongingNetworkAssociation, IpNetworkEntity)\
        .where(BelongingNetworkAssociation.entry_id == ee.id)
    if len(query) != 1:
        raise ValueError
    for row in query:
        ine = row.network
        q = HasAssociation.select()\
            .join_from(HasAssociation, EntryIpAsDatabaseEntity)\
            .join_from(HasAssociation, IpRangeEntity)\
            .where(HasAssociation.entry_id == ee.id)
        if len(q) != 1:
            raise ValueError
        for r in q:
            ire = r.range
            return ee, ire, ine
        break


def has_belonging_network(ee: EntryIpAsDatabaseEntity) -> IpNetworkEntity:
    query = IpNetworkEntity.select()\
        .join_from(IpNetworkEntity, BelongingNetworkAssociation)\
        .where(BelongingNetworkAssociation.entry == ee)
    if len(query) == 0:
        raise ValueError
    elif len(query) > 1:
        raise ValueError
    for row in query:
        return row
