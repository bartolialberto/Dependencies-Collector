from typing import List
from peewee import DoesNotExist
from persistence import helper_website
from persistence.BaseModel import WebSiteEntity, WebSiteLandsAssociation, DomainNameEntity, WebServerEntity, UrlEntity


"""
def insert(wee: WebSiteEntity, lpe: LandingPageEntity or None, https: bool) -> WebSiteLandsAssociation:
    wsla, created = WebSiteLandsAssociation.get_or_create(website=wee, landing_page=lpe, https=https)
    try:
        wsla = WebSiteLandsAssociation.get(WebSiteLandsAssociation.website == wee, WebSiteLandsAssociation.landing_page == lpe)
    except DoesNotExist:
        wsla = WebSiteLandsAssociation.create(website=wee, landing_page=lpe, https=https)
    return wsla
"""


def insert(wsitee: WebSiteEntity, wservere: WebServerEntity or None, https: bool) -> WebSiteLandsAssociation:
    wsla, created = WebSiteLandsAssociation.get_or_create(website=wsitee, webserver=wservere, https=https)
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
    result = list()
    query = WebSiteLandsAssociation.select()\
        .join_from(WebSiteLandsAssociation, WebSiteEntity)\
        .where(WebSiteLandsAssociation.website == wse)
    for row in query:
        result.append(row)
    return result


def get_all_from_website_entity(wse: WebSiteEntity) -> List[WebSiteLandsAssociation]:
    result = list()
    query = WebSiteLandsAssociation.select()\
        .join_from(WebSiteLandsAssociation, WebSiteEntity)\
        .where(WebSiteLandsAssociation.website == wse)
    for row in query:
        result.append(row)
    return result


def delete_all_from_string_website(website: str):
    try:
        tmp = get_all_from_string_website(website)
        for relation in tmp:
            relation.delete_instance()
    except DoesNotExist:
        pass


def delete_all_from_website_entity(wse: WebSiteEntity):
    try:
        tmp = get_all_from_website_entity(wse)
        for relation in tmp:
            relation.delete_instance()
    except DoesNotExist:
        pass


def get_first_from_string_website(website_url: str) -> WebSiteLandsAssociation:
    try:
        wse = helper_website.get(website_url)
    except DoesNotExist:
        raise
    try:
        wsla = WebSiteLandsAssociation.get(WebSiteLandsAssociation.website == wse)
    except DoesNotExist:
        raise
    return wsla


def get_first_from_website_entity(wse: WebSiteEntity) -> WebSiteLandsAssociation:
    try:
        wsla = WebSiteLandsAssociation.get(WebSiteLandsAssociation.website == wse)
    except DoesNotExist:
        raise
    return wsla


def get_first_from_string_website_and_https_flag(website_url: str, https: bool) -> WebSiteLandsAssociation:
    try:
        wse = helper_website.get(website_url)
    except DoesNotExist:
        raise
    try:
        wsla = WebSiteLandsAssociation.get(WebSiteLandsAssociation.website == wse, WebSiteLandsAssociation.https == https)
    except DoesNotExist:
        raise
    return wsla


def get_first_from_website_entity_and_https_flag(wse: WebSiteEntity, https: bool) -> WebSiteLandsAssociation:
    try:
        wsla = WebSiteLandsAssociation.get(WebSiteLandsAssociation.website == wse, WebSiteLandsAssociation.https == https)
    except DoesNotExist:
        raise
    return wsla
