from typing import Set
from persistence.BaseModel import ScriptEntity, ScriptWithdrawAssociation, WebSiteEntity


def insert(url: str) -> ScriptEntity:
    se, created = ScriptEntity.get_or_create(src=url)
    return se


def get_from_web_site_and_scheme(wse: WebSiteEntity, https: bool) -> Set[ScriptEntity]:
    query = ScriptWithdrawAssociation.select()\
        .where((ScriptWithdrawAssociation.https == https) & (ScriptWithdrawAssociation.web_site == wse))
    result = set()
    for row in query:
        result.add(row.script)
    return result
