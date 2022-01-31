from typing import Set
from peewee import DoesNotExist
from exceptions.InvalidUrlError import InvalidUrlError
from persistence import helper_url
from persistence.BaseModel import WebSiteEntity, ScriptServerEntity, ScriptSiteLandsAssociation, \
    ScriptHostedOnAssociation, ScriptWithdrawAssociation, WebServerEntity, WebSiteLandsAssociation
from utils import url_utils


def insert(url: str) -> WebSiteEntity:
    ue = helper_url.insert(url)
    we, created = WebSiteEntity.get_or_create(url=ue)
    return we


def get(url: str) -> WebSiteEntity:
    try:
        temp = url_utils.deduct_second_component(url)
    except InvalidUrlError:
        raise
    try:
        ue = helper_url.get(temp)
    except DoesNotExist:
        raise
    try:
        return WebSiteEntity.get(WebSiteEntity.url == ue)
    except DoesNotExist:
        raise


def get_all_from_entity_script_server(sse: ScriptServerEntity) -> Set[WebSiteEntity]:
    query = ScriptWithdrawAssociation.select()\
        .join(ScriptHostedOnAssociation, on=(ScriptWithdrawAssociation.script == ScriptHostedOnAssociation.script))\
        .join(ScriptSiteLandsAssociation, on=(ScriptHostedOnAssociation.script_site == ScriptSiteLandsAssociation.script_site))\
        .where((ScriptSiteLandsAssociation.script_server == sse) & (ScriptWithdrawAssociation.script.is_null(False)))
    result = set()
    for row in query:
        result.add(row.web_site)
    return result


def get_all_from_entity_web_server(wse: WebServerEntity) -> Set[WebSiteEntity]:
    query = WebSiteLandsAssociation.select()\
        .where(WebSiteLandsAssociation.web_server == wse)
    result = set()
    for row in query:
        result.add(row.web_site)
    return result


def get_everyone() -> Set[WebSiteEntity]:
    query = WebSiteEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result
