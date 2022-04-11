from entities.RowPrefixesTable import RowPrefixesTable
from persistence.BaseModel import ROVEntity


def insert(row: RowPrefixesTable) -> ROVEntity:
    re, created = ROVEntity.get_or_create(state=row.rov_state.to_string(), visibility=row.visibility)
    return re
