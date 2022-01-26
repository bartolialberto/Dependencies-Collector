from typing import List, Set
from peewee import DoesNotExist

from persistence import helper_url, helper_web_site
from persistence.BaseModel import WebSiteEntity, WebSiteLandsAssociation, WebServerEntity, UrlEntity, IpAddressEntity


def insert(wsitee: WebSiteEntity, wservere: WebServerEntity or None, https: bool) -> WebSiteLandsAssociation:
    wsla, created = WebSiteLandsAssociation.get_or_create(web_site=wsitee, web_server=wservere, https=https)
    return wsla


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
        .where(WebSiteLandsAssociation.web_site == wse)
    for row in query:
        result.append(row)
    return result


def get_all_from_string_website_and_scheme(website: str, https: bool) -> List[WebSiteLandsAssociation]:
    try:
        wse = helper_web_site.get(website)
    except DoesNotExist:
        raise
    return get_all_from_entity_web_site_and_scheme(wse, https)


def get_all_from_entity_web_site_and_scheme(wse: WebSiteEntity, https: bool) -> List[WebSiteLandsAssociation]:
    result = list()
    query = WebSiteLandsAssociation.select()\
        .where((WebSiteLandsAssociation.web_site == wse) &
               (WebSiteLandsAssociation.https == https))
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
               (WebSiteLandsAssociation.https == wsla.https))
    query.execute()


def get_unresolved(https: bool) -> Set[WebSiteLandsAssociation]:
    query = WebSiteLandsAssociation.select()\
        .where((WebSiteLandsAssociation.web_server.is_null(True)) & (WebSiteLandsAssociation.https == https))
    result = set()
    for row in query:
        result.add(row)
    return result
