from typing import List, Set, Dict, Union
from peewee import DoesNotExist
from entities.SchemeUrl import SchemeUrl
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence.BaseModel import WebSiteEntity, WebSiteLandsAssociation, WebServerEntity, db


def insert(wsitee: WebSiteEntity, starting_https: bool, landing_url: Union[SchemeUrl, None], wservere: Union[WebServerEntity, None]) -> WebSiteLandsAssociation:
    if landing_url is None:
        landing_url_string = None
        landing_scheme_is_https = None
    else:
        landing_url_string = landing_url.string
        landing_scheme_is_https = landing_url.is_https()
    wsla, created = WebSiteLandsAssociation.get_or_create(web_site=wsitee, starting_https=starting_https, landing_url=landing_url_string, web_server=wservere, landing_https=landing_scheme_is_https)
    return wsla


def final_bulk_insert(fields: List[Dict[str, WebSiteEntity or bool or WebServerEntity or None]]) -> None:
    with db.atomic():
        count_inserts = WebSiteLandsAssociation.insert_many(fields).on_conflict_ignore().execute()


def bulk_insert(fields: List[Dict[str, WebSiteEntity or bool or WebServerEntity or None]]) -> None:
    with db.atomic():
        count_inserts = WebSiteLandsAssociation.insert_many(fields).on_conflict_ignore().execute()
        count_inserts = WebSiteLandsAssociation.insert_many(fields).on_conflict_ignore().execute()


def test_getting_unlimited_association_from(wse: WebSiteEntity) -> Set[WebSiteLandsAssociation]:
    result = set()
    query = WebSiteLandsAssociation.select()\
        .where(WebSiteLandsAssociation.web_site == wse)
    for row in query:
        result.add(row)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result


def get_from_web_site_and_starting_scheme(wse: WebSiteEntity, is_https: bool) -> WebSiteLandsAssociation:
    try:
        return WebSiteLandsAssociation.get((WebSiteLandsAssociation.web_site == wse) & (WebSiteLandsAssociation.starting_https == is_https))
    except DoesNotExist:
        raise


def get_all_from_entity_web_site(wse: WebSiteEntity) -> List[WebSiteLandsAssociation]:
    result = list()
    query = WebSiteLandsAssociation.select()\
        .where((WebSiteLandsAssociation.web_site == wse) & (WebSiteLandsAssociation.web_server.is_null(False)))
    for row in query:
        result.append(row)
    return result


def get_all_from_entity_web_site_and_scheme(wse: WebSiteEntity, https: bool) -> List[WebSiteLandsAssociation]:
    result = list()
    query = WebSiteLandsAssociation.select()\
        .where((WebSiteLandsAssociation.web_site == wse) &
               (WebSiteLandsAssociation.https == https) &
               (WebSiteLandsAssociation.web_server.is_null(False)))
    for row in query:
        result.append(row)
    return result


def delete_all_from_entity_web_site(wse: WebSiteEntity):
    try:
        tmp = get_all_from_entity_web_site(wse)
        for relation in tmp:
            relation.delete_instance()
    except DoesNotExist:
        pass


def get_unresolved() -> Set[WebSiteLandsAssociation]:
    query = WebSiteLandsAssociation.select()\
        .where(WebSiteLandsAssociation.web_server.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
