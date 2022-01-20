from typing import List
from peewee import DoesNotExist
from persistence import helper_web_site
from persistence.BaseModel import WebSiteEntity, WebSiteLandsAssociation, DomainNameEntity, WebServerEntity, UrlEntity, \
    IpAddressEntity


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
