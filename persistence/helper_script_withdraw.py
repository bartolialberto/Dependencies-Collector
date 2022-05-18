from typing import Set, List, Dict, Union, Optional
from peewee import DoesNotExist, chunked
from persistence.BaseModel import WebSiteEntity, ScriptEntity, ScriptWithdrawAssociation, BATCH_SIZE_MAX, \
    NORMALIZATION_CONSTANT


def insert(wse: WebSiteEntity, se: Optional[ScriptEntity], https: bool, integrity: Optional[str]) -> ScriptWithdrawAssociation:
    swa, created = ScriptWithdrawAssociation.get_or_create(script=se, web_site=wse, integrity=integrity, https=https)
    return swa


# insert + update = upsert
def bulk_upserts(data_source: List[Dict[str, Union[ScriptEntity, bool, str, None]]]) -> None:
    """
    Must be invoked inside a peewee transaction. Transaction needs the database object (db).
    Example:
        with db.atomic() as transaction:
            bulk_upserts(...)

    :param data_source: Fields name and values of multiple ScriptWithdrawAssociation objects in the form of a
    dictionary.
    :type data_source: List[Dict[str, Union[ScriptEntity, bool, str, None]]]
    """
    num_of_fields = 4
    batch_size = int(BATCH_SIZE_MAX / (num_of_fields + NORMALIZATION_CONSTANT))
    for batch in chunked(data_source, batch_size):
        ScriptWithdrawAssociation.insert_many(batch).on_conflict_replace().execute()


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
