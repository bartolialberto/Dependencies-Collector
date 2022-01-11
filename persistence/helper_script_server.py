from persistence import helper_url
from persistence.BaseModel import ScriptServerEntity


def insert(url: str) -> ScriptServerEntity:
    ue = helper_url.insert(url)
    sse, created = ScriptServerEntity.get_or_create(url=ue)
    return sse