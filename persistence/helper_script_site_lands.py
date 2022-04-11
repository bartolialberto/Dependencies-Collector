from typing import List, Set, Union
from peewee import DoesNotExist
from entities.SchemeUrl import SchemeUrl
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence.BaseModel import ScriptSiteEntity, ScriptServerEntity, ScriptSiteLandsAssociation


def insert(ssitee: ScriptSiteEntity, starting_https: bool, landing_url: Union[SchemeUrl, None], sservere: Union[ScriptServerEntity, None]) -> ScriptSiteLandsAssociation:
    if landing_url is None:
        if sservere is not None:
            raise ValueError
        landing_url_string = None
        landing_scheme_is_https = None
    else:
        if landing_url is None:
            raise ValueError
        if sservere.name.string != landing_url.domain_name().string:
            raise ValueError
        landing_url_string = landing_url.string
        landing_scheme_is_https = landing_url.is_https()
    ssla, created = ScriptSiteLandsAssociation.get_or_create(script_site=ssitee, starting_https=starting_https, landing_url=landing_url_string, script_server=sservere, landing_https=landing_scheme_is_https)
    return ssla


# insert + update = upsert
def upsert(ssitee: ScriptSiteEntity, starting_https: bool, landing_url: Union[SchemeUrl, None], sservere: Union[ScriptServerEntity, None]) -> None:
    if landing_url is None:
        if sservere is not None:
            raise ValueError
        landing_url_string = None
        landing_scheme_is_https = None
    else:
        if landing_url is None:
            raise ValueError
        if sservere.name.string != landing_url.domain_name().string:
            raise ValueError
        landing_url_string = landing_url.string
        landing_scheme_is_https = landing_url.is_https()
    ScriptSiteLandsAssociation.replace(script_site=ssitee, starting_https=starting_https, landing_url=landing_url_string, script_server=sservere, landing_https=landing_scheme_is_https).execute()


def get_all_from_entity_script_site_and_scheme(sse: ScriptSiteEntity, https: bool) -> List[ScriptSiteLandsAssociation]:
    result = list()
    query = ScriptSiteLandsAssociation.select()\
        .where((ScriptSiteLandsAssociation.script_site == sse) &
            (ScriptSiteLandsAssociation.https == https) &
            (ScriptSiteLandsAssociation.script_server.is_null(False)))
    for row in query:
        result.append(row)
    return result


def get_from_script_site_and_starting_scheme(sse: ScriptSiteEntity, is_https: bool) -> ScriptSiteLandsAssociation:
    try:
        return ScriptSiteLandsAssociation.get((ScriptSiteLandsAssociation.script_site == sse) & (ScriptSiteLandsAssociation.starting_https == is_https))
    except DoesNotExist:
        raise


def test_getting_unlimited_association_from(sse: ScriptSiteEntity) -> Set[ScriptSiteLandsAssociation]:
    result = set()
    query = ScriptSiteLandsAssociation.select()\
        .where(ScriptSiteLandsAssociation.script_site == sse)
    for row in query:
        result.add(row)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result


def delete_unresolved_row_for(sse: ScriptSiteEntity, starting_https: bool) -> None:
    try:
        ssla = ScriptSiteLandsAssociation.get((ScriptSiteLandsAssociation.script_site == sse) & (ScriptSiteLandsAssociation.starting_https == starting_https) & (ScriptSiteLandsAssociation.script_server.is_null(True)))
        ssla.delete_instance()
    except DoesNotExist:
        pass


def get_unresolved() -> Set[ScriptSiteLandsAssociation]:
    query = ScriptSiteLandsAssociation.select()\
        .where(ScriptSiteLandsAssociation.script_server.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
