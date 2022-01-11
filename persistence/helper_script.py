from persistence.BaseModel import ScriptEntity


def insert(url: str) -> ScriptEntity:
    se, created = ScriptEntity.get_or_create(src=url)
    return se
