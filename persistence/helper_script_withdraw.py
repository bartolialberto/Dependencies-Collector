from typing import Set
from peewee import DoesNotExist
from persistence.BaseModel import WebSiteEntity, ScriptEntity, ScriptWithdrawAssociation


def insert(wse: WebSiteEntity, se: ScriptEntity or None, https: bool, integrity: str or None) -> ScriptWithdrawAssociation:
    swa, created = ScriptWithdrawAssociation.get_or_create(script=se, web_site=wse, integrity=integrity, https=https)
    return swa


def get_all_of(wse: WebSiteEntity, https: bool) -> Set[ScriptWithdrawAssociation]:
    """ Query probably useful only for tests. """
    query = ScriptWithdrawAssociation.select()\
        .where((ScriptWithdrawAssociation.web_site == wse) &
               (ScriptWithdrawAssociation.https == https))
    result = set()
    for row in query:
        result.add(row)
    return result


def delete_unresolved_row_for(wse: WebSiteEntity, https: bool) -> None:
    try:
        swa = ScriptWithdrawAssociation.get((ScriptWithdrawAssociation.web_site == wse) & (ScriptWithdrawAssociation.https == https) & (ScriptWithdrawAssociation.script.is_null(True)))
        swa.delete_instance()
    except DoesNotExist:
        pass


def get_unresolved() -> Set[ScriptWithdrawAssociation]:
    query = ScriptWithdrawAssociation.select()\
        .where(ScriptWithdrawAssociation.script.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
