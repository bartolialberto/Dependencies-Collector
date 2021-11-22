from entities.ROVPageScraper import RowPrefixesTable
from persistence.BaseModel import EntryIpAsDatabaseEntity, MatchesAssociation, NameserverEntity, EntryROVPageEntity


def insert_or_get_only_entry_ip_as_db(n: NameserverEntity, eia: EntryIpAsDatabaseEntity):
    ma, created = MatchesAssociation.get_or_create(nameserver=n.id, entry_rov_page=None, entry_ip_as_database=eia.id)


def insert_or_get_only_entry_rov_page(nameserver: str, row: RowPrefixesTable):
    n = NameserverEntity.get(NameserverEntity.name == nameserver)
    e, created = EntryROVPageEntity.get_or_create(autonomous_system_number=row.as_number, visibility=row.visibility, rov_state=row.rov_state.to_string())
    ma = MatchesAssociation.get(MatchesAssociation.nameserver == n.id)
    ma.entry_rov_page = e.id
    ma.save()
