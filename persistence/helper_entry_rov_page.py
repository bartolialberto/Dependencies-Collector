from entities.ROVPageScraper import RowPrefixesTable
from persistence.BaseModel import EntryROVPageEntity


def insert(row: RowPrefixesTable) -> EntryROVPageEntity:
    e, created = EntryROVPageEntity.get_or_create(autonomous_system_number=row.as_number, visibility=row.visibility, rov_state=row.rov_state.to_string())
    return e


