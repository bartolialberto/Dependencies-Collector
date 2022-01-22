from typing import Set
from persistence.BaseModel import WebSiteEntity, ScriptEntity, ScriptWithdrawAssociation


def insert(wse: WebSiteEntity, se: ScriptEntity or None, https: bool, integrity: str or None) -> ScriptWithdrawAssociation:
    swa, created = ScriptWithdrawAssociation.get_or_create(script=se, web_site=wse, integrity=integrity, https=https)
    return swa


def get_unresolved() -> Set[ScriptWithdrawAssociation]:
    query = ScriptWithdrawAssociation.select()\
        .where(ScriptWithdrawAssociation.script.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
