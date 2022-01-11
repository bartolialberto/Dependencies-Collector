from typing import List, Tuple
from peewee import DoesNotExist
from persistence import helper_url, helper_web_site, helper_web_site_lands
from persistence.BaseModel import WebServerEntity, WebSiteEntity, WebSiteLandsAssociation
from utils import url_utils

"""
def insert(lpe: LandingPageEntity) -> WebServerEntity:
    domain_name = domain_name_utils.deduct_domain_name(lpe.url)
    url = helper_url.insert()
    de = helper_domain_name.insert(domain_name)
    wse, created = WebServerEntity.get_or_create(name=de)
    return wse
"""


def insert(url: str) -> WebServerEntity:
    ue = helper_url.insert(url)
    we, created = WebServerEntity.get_or_create(url=ue)
    return we


def get(url: str) -> WebServerEntity:
    temp = url_utils.deduct_second_component(url)
    try:
        ue = helper_url.get(temp)
    except DoesNotExist:
        raise
    try:
        return WebServerEntity.get(WebServerEntity.url == ue)
    except DoesNotExist:
        raise


def get_from_string_website(website_url: str) -> List[WebServerEntity]:
    try:
        wse = helper_web_site.get(website_url)
    except DoesNotExist:
        raise

    query = WebSiteLandsAssociation.select()\
        .join_from(WebSiteLandsAssociation, WebSiteEntity)\
        .join_from(WebSiteLandsAssociation, WebServerEntity)\
        .where(WebSiteLandsAssociation.web_site == wse)

    result = list()
    for row in query:
        result.append(row.server)
    return result


def get_from_website_entity(wse: WebSiteEntity) -> List[WebServerEntity]:
    query = WebSiteLandsAssociation.select()\
        .join_from(WebSiteLandsAssociation, WebSiteEntity)\
        .join_from(WebSiteLandsAssociation, WebServerEntity)\
        .where(WebSiteLandsAssociation.web_site == wse)

    result = list()
    for row in query:
        result.append(row.server)
    return result


def get_first_from_string_website_and_https_flag(website: str, https: bool) -> WebServerEntity:
    try:
        wla = helper_web_site_lands.get_first_from_string_website_and_https_flag(website, https)
    except DoesNotExist:
        raise
    return WebServerEntity.get_by_id(wla.web_server)
