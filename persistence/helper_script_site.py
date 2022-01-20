from typing import Set
from peewee import DoesNotExist
from persistence import helper_url
from persistence.BaseModel import ScriptSiteEntity, ScriptSiteLandsAssociation


def insert(url: str) -> ScriptSiteEntity:
    ue = helper_url.insert(url)
    sse, created = ScriptSiteEntity.get_or_create(url=ue)
    return sse


def get(url: str) -> ScriptSiteEntity:
    try:
        ue = helper_url.get(url)
    except DoesNotExist:
        raise
    sse = ScriptSiteEntity.get(ScriptSiteEntity.url == ue)
    return sse


def get_unresolved() -> Set[ScriptSiteEntity]:
    query = ScriptSiteLandsAssociation.select()\
        .join_from(ScriptSiteLandsAssociation, ScriptSiteEntity)\
        .where(ScriptSiteLandsAssociation.script_server == None, ScriptSiteLandsAssociation.ip_address == None)
    result = set()
    for row in query:
        result.add(row.web_site)
    return result
