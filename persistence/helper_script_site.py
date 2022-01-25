from typing import Set
from peewee import DoesNotExist
from persistence import helper_url, helper_web_site
from persistence.BaseModel import ScriptSiteEntity, WebSiteEntity, ScriptHostedOnAssociation, ScriptWithdrawAssociation


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


def get_from_string_web_site(web_site: str) -> Set[ScriptSiteEntity]:
    try:
        wse = helper_web_site.get(web_site)
    except DoesNotExist:
        raise
    return get_from_entity_web_site(wse)


def get_from_entity_web_site(wse: WebSiteEntity) -> Set[ScriptSiteEntity]:
    query = ScriptHostedOnAssociation.select()\
        .join(ScriptWithdrawAssociation, on=(ScriptHostedOnAssociation.script == ScriptWithdrawAssociation.script))\
        .where(ScriptWithdrawAssociation.web_site == wse)
    result = set()
    for row in query:
        result.add(row.script_site)
    return result
