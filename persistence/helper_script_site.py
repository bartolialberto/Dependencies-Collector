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


def get_https_unresolved() -> Set[ScriptSiteEntity]:
    query = ScriptSiteLandsAssociation.select()\
        .join_from(ScriptSiteLandsAssociation, ScriptSiteEntity)\
        .where((ScriptSiteLandsAssociation.script_server.is_null(True)) & (ScriptSiteLandsAssociation.ip_address.is_null(True)) & (ScriptSiteLandsAssociation.https == True))
    result = set()
    for row in query:
        result.add(row.script_site)
    return result


def get_http_unresolved() -> Set[ScriptSiteEntity]:
    query = ScriptSiteLandsAssociation.select()\
        .join_from(ScriptSiteLandsAssociation, ScriptSiteEntity)\
        .where((ScriptSiteLandsAssociation.script_server.is_null(True)) & (ScriptSiteLandsAssociation.ip_address.is_null(True)) & (ScriptSiteLandsAssociation.https == False))
    result = set()
    for row in query:
        result.add(row.script_site)
    return result
