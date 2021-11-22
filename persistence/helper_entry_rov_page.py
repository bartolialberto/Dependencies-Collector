from entities.ROVPageScraper import RowPrefixesTable
from persistence.BaseModel import EntryROVPageEntity


def insert(entry: RowPrefixesTable) -> EntryROVPageEntity:
    e, created = EntryROVPageEntity.get_or_create(autonomous_system_number=entry.as_number, visibility=entry.visibility, rov_state=entry.rov_state.to_string())
    return e


