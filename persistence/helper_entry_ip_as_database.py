from entities.IpAsDatabase import EntryIpAsDatabase
from persistence.BaseModel import EntryIpAsDatabaseEntity, MatchesAssociation, NameserverEntity, EntryROVPageEntity


def insert_or_get(entry: EntryIpAsDatabase) -> EntryIpAsDatabaseEntity:
    e, created = EntryIpAsDatabaseEntity.get_or_create(autonomous_system_number=entry.as_number, country_code=entry.country_code, autonomous_system_description=entry.as_description)
    return e
