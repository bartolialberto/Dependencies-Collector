from persistence.BaseModel import ROVEntity


def insert(state_string: str, visibility_int: int) -> ROVEntity:
    re, created = ROVEntity.get_or_create(state=state_string, visibility=visibility_int)
    return re
