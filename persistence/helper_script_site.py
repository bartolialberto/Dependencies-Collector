from typing import Set
from peewee import DoesNotExist

from entities.Url import Url
from persistence import helper_url, helper_web_site
from persistence.BaseModel import ScriptSiteEntity, WebSiteEntity, ScriptHostedOnAssociation, ScriptWithdrawAssociation


def insert(url: Url) -> ScriptSiteEntity:
    ue = helper_url.insert(url)
    sse, created = ScriptSiteEntity.get_or_create(url=ue)
    return sse


def get(url: Url) -> ScriptSiteEntity:
    try:
        ue = helper_url.get(url)
    except DoesNotExist:
        raise
    sse = ScriptSiteEntity.get(ScriptSiteEntity.url == ue)
    return sse


def get_from_string_web_site(web_site: str) -> Set[ScriptSiteEntity]:
    web_site_url = Url(web_site)
    try:
        wse = helper_web_site.get(web_site_url)
    except DoesNotExist:
        raise
    return get_from_entity_web_site(wse)


def get_from_entity_web_site(wse: WebSiteEntity) -> Set[ScriptSiteEntity]:
    query = ScriptHostedOnAssociation.select()\
        .join(ScriptWithdrawAssociation, on=(ScriptHostedOnAssociation.script == ScriptWithdrawAssociation.script))\
        .where((ScriptWithdrawAssociation.web_site == wse) & (ScriptWithdrawAssociation.script.is_null(False)))
    result = set()
    for row in query:
        result.add(row.script_site)
    return result
