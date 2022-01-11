from persistence import helper_url
from persistence.BaseModel import ScriptSiteEntity


def insert(url: str) -> ScriptSiteEntity:
    ue = helper_url.insert(url)
    sse, created = ScriptSiteEntity.get_or_create(url=ue)
    return sse
