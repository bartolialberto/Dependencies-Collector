from typing import List, Dict, Union
from peewee import chunked
from persistence.BaseModel import ScriptEntity, ScriptSiteEntity, ScriptHostedOnAssociation, BATCH_SIZE_MAX, \
    NORMALIZATION_CONSTANT


def insert(se: ScriptEntity, sse: ScriptSiteEntity) -> ScriptHostedOnAssociation:
    shoa, created = ScriptHostedOnAssociation.get_or_create(script=se, script_site=sse)
    return shoa


# insert + update = upsert
def bulk_upserts(data_source: List[Dict[str, Union[ScriptEntity, ScriptSiteEntity]]]) -> None:
    """
    Must be invoked inside a peewee transaction. Transaction needs the database object (db).
    Example:
        with db.atomic() as transaction:
            bulk_upserts(...)

    :param data_source: Fields name and values of multiple ScriptHostedOnAssociation objects in the form of a
    dictionary.
    :type data_source: List[Dict[str, Union[ScriptEntity, ScriptSiteEntity]]]
    """
    num_of_fields = 2
    batch_size = int(BATCH_SIZE_MAX / (num_of_fields + NORMALIZATION_CONSTANT))
    for batch in chunked(data_source, batch_size):
        ScriptHostedOnAssociation.insert_many(batch).on_conflict_replace().execute()
