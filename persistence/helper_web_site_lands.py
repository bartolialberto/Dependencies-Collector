from typing import List, Set, Dict
from peewee import DoesNotExist
from entities.Url import Url
from persistence import helper_web_site
from persistence.BaseModel import WebSiteEntity, WebSiteLandsAssociation, WebServerEntity, UrlEntity, db


def insert(wsitee: WebSiteEntity, starting_https: bool, wservere: WebServerEntity or None, landing_https: bool or None) -> WebSiteLandsAssociation:
    wsla, created = WebSiteLandsAssociation.get_or_create(web_site=wsitee, starting_https=starting_https, web_server=wservere, landing_https=landing_https)
    return wsla


def final_bulk_insert(fields: List[Dict[str, WebSiteEntity or bool or WebServerEntity or None]]) -> None:
    with db.atomic():
        count_inserts = WebSiteLandsAssociation.insert_many(fields).on_conflict_ignore().execute()


def bulk_insert(fields: List[Dict[str, WebSiteEntity or bool or WebServerEntity or None]]) -> None:
    with db.atomic():
        count_inserts = WebSiteLandsAssociation.insert_many(fields).on_conflict_ignore().execute()
        count_inserts = WebSiteLandsAssociation.insert_many(fields).on_conflict_ignore().execute()


def get_all_from_string_website(website: str) -> List[WebSiteLandsAssociation]:
    try:
        ue = UrlEntity.get(UrlEntity.string == website)
    except DoesNotExist:
        raise
    try:
        wse = WebSiteEntity.get(WebSiteEntity.url == ue)
    except DoesNotExist:
        raise
    return get_all_from_entity_web_site(wse)


def get_all_from_entity_web_site(wse: WebSiteEntity) -> List[WebSiteLandsAssociation]:
    result = list()
    query = WebSiteLandsAssociation.select()\
        .where((WebSiteLandsAssociation.web_site == wse) & (WebSiteLandsAssociation.web_server.is_null(False)))
    for row in query:
        result.append(row)
    return result


def get_all_from_string_website_and_scheme(website: Url, https: bool) -> List[WebSiteLandsAssociation]:
    try:
        wse = helper_web_site.get(website)
    except DoesNotExist:
        raise
    return get_all_from_entity_web_site_and_scheme(wse, https)


def get_all_from_entity_web_site_and_scheme(wse: WebSiteEntity, https: bool) -> List[WebSiteLandsAssociation]:
    result = list()
    query = WebSiteLandsAssociation.select()\
        .where((WebSiteLandsAssociation.web_site == wse) &
               (WebSiteLandsAssociation.https == https) &
               (WebSiteLandsAssociation.web_server.is_null(False)))
    for row in query:
        result.append(row)
    return result


def delete_all_from_string_website(website: str):
    try:
        ue = UrlEntity.get(UrlEntity.string == website)
    except DoesNotExist:
        raise
    try:
        wse = WebSiteEntity.get(WebSiteEntity.url == ue)
    except DoesNotExist:
        raise
    return delete_all_from_entity_web_site(wse)


def delete_all_from_entity_web_site(wse: WebSiteEntity):
    try:
        tmp = get_all_from_entity_web_site(wse)
        for relation in tmp:
            relation.delete_instance()
    except DoesNotExist:
        pass


def update(wsla: WebSiteLandsAssociation, new_w_server_e: WebServerEntity) -> None:
    query = WebSiteLandsAssociation.update(web_server=new_w_server_e) \
        .where((WebSiteLandsAssociation.web_site == wsla.web_site) &
               (WebSiteLandsAssociation.https == wsla.https) &
               (WebSiteLandsAssociation.web_server.is_null(False)))
    query.execute()


def get_unresolved() -> Set[WebSiteLandsAssociation]:
    query = WebSiteLandsAssociation.select()\
        .where(WebSiteLandsAssociation.web_server.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
