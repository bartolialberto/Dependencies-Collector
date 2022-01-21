from typing import List, Set
from peewee import DoesNotExist
from persistence.BaseModel import WebSiteEntity, WebSiteLandsAssociation, WebServerEntity, UrlEntity, IpAddressEntity


def insert(wsitee: WebSiteEntity, wservere: WebServerEntity or None, https: bool, iae: IpAddressEntity or None) -> WebSiteLandsAssociation:
    wsla, created = WebSiteLandsAssociation.get_or_create(web_site=wsitee, web_server=wservere, https=https, ip_address=iae)
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
        .join_from(WebSiteLandsAssociation, WebSiteEntity)\
        .where(WebSiteLandsAssociation.web_site == wse)
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


def update(wsla: WebSiteLandsAssociation, new_w_server_e: WebServerEntity, new_ip_address: IpAddressEntity) -> None:
    query = WebSiteLandsAssociation.update(web_server=new_w_server_e, ip_address=new_ip_address) \
        .where((WebSiteLandsAssociation.web_site == wsla.web_site) &
               (WebSiteLandsAssociation.https == wsla.https))
    query.execute()


def get_unresolved(https: bool) -> Set[WebSiteLandsAssociation]:
    query = WebSiteLandsAssociation.select()\
        .join_from(WebSiteLandsAssociation, WebSiteEntity)\
        .where((WebSiteLandsAssociation.web_server.is_null(True)) & (WebSiteLandsAssociation.ip_address.is_null(True)) & (WebSiteLandsAssociation.https == https))
    result = set()
    for row in query:
        result.add(row)
    return result
