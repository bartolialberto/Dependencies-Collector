from entities.ROVPageScraper import RowPrefixesTable
from persistence.BaseModel import EntryIpAsDatabaseEntity, MatchesAssociation, NameserverEntity, EntryROVPageEntity


def insert_or_get_only_entry_ip_as_db(n: NameserverEntity, eia: EntryIpAsDatabaseEntity):
    ma, created = MatchesAssociation.get_or_create(nameserver=n.id, entry_rov_page=None, entry_ip_as_database=eia.id)


def insert_or_get(n: NameserverEntity, eia: EntryIpAsDatabaseEntity, erp: EntryROVPageEntity):
    ma, created = MatchesAssociation.get_or_create(nameserver=n.id, entry_rov_page=erp.id, entry_ip_as_database=eia.id)


def insert_or_get_only_entry_rov_page(nameserver: str, e: EntryROVPageEntity):
    n = NameserverEntity.get(NameserverEntity.name == nameserver)
    ma = MatchesAssociation.get(MatchesAssociation.nameserver == n.id)
    ma.entry_rov_page = e.id
    ma.save()
