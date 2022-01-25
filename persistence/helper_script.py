from typing import Set, List
from peewee import DoesNotExist
from persistence import helper_web_site
from persistence.BaseModel import ScriptEntity, ScriptWithdrawAssociation, WebSiteEntity


def insert(url: str) -> ScriptEntity:
    se, created = ScriptEntity.get_or_create(src=url)
    return se


def get_from(web_site: str) -> List[ScriptEntity]:
    # from landing using HTTPS and HTTP
    # no integrity and https attribute check
    try:
        wse = helper_web_site.get(web_site)
    except DoesNotExist:
        raise
    query = ScriptWithdrawAssociation.select()\
        .where(ScriptWithdrawAssociation.web_site == wse)
    result = list()
    for row in query:
        result.append(row.script)
    return result


def get_from_with_scheme(web_site: str, https: bool) -> Set[ScriptEntity]:
    # no integrity attribute check
    try:
        wse = helper_web_site.get(web_site)
    except DoesNotExist:
        raise
    query = ScriptWithdrawAssociation.select()\
        .where((ScriptWithdrawAssociation.https == https) & (ScriptWithdrawAssociation.web_site == wse))
    result = set()
    for row in query:
        result.add(row.script)
    return result


def get_from_with_scheme_and_integrity(web_site: str, https: bool) -> Set[ScriptEntity]:
    try:
        wse = helper_web_site.get(web_site)
    except DoesNotExist:
        raise
    query = ScriptWithdrawAssociation.select()\
        .where((ScriptWithdrawAssociation.https == https) & (ScriptWithdrawAssociation.web_site == wse) & (ScriptWithdrawAssociation.integrity.is_null(False)))
    result = set()
    for row in query:
        result.add(row.script)
    return result
