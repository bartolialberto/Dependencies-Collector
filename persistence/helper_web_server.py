from typing import List, Tuple, Set
from peewee import DoesNotExist
from persistence import helper_url, helper_web_site, helper_web_site_lands, helper_domain_name
from persistence.BaseModel import WebServerEntity, WebSiteEntity, WebSiteLandsAssociation
from utils import url_utils, domain_name_utils

"""
def insert(lpe: LandingPageEntity) -> WebServerEntity:
    domain_name = domain_name_utils.deduct_domain_name(lpe.url)
    url = helper_url.insert()
    de = helper_domain_name.insert(domain_name)
    wse, created = WebServerEntity.get_or_create(name=de)
    return wse
"""


def insert(name: str) -> WebServerEntity:
    dn = domain_name_utils.insert_trailing_point(name)
    dne = helper_domain_name.insert(dn)
    we, created = WebServerEntity.get_or_create(name=dne)
    return we


def get(name: str) -> WebServerEntity:
    dn = domain_name_utils.insert_trailing_point(name)
    try:
        dne = helper_domain_name.get(dn)
    except DoesNotExist:
        raise
    try:
        return WebServerEntity.get(WebServerEntity.name == dne)
    except DoesNotExist:
        raise


def get_from_string_website(website_url: str) -> List[WebServerEntity]:
    try:
        wse = helper_web_site.get(website_url)
    except DoesNotExist:
        raise

    query = WebSiteLandsAssociation.select()\
        .join_from(WebSiteLandsAssociation, WebServerEntity)\
        .where(WebSiteLandsAssociation.web_site == wse)

    result = list()
    for row in query:
        result.append(row.web_server)
    return result


def get_from_website_entity(wse: WebSiteEntity) -> List[WebServerEntity]:
    query = WebSiteLandsAssociation.select()\
        .join_from(WebSiteLandsAssociation, WebServerEntity)\
        .where(WebSiteLandsAssociation.web_site == wse)

    result = list()
    for row in query:
        result.append(row.web_server)
    return result


def get_from(website_param: str or WebSiteEntity, https: bool, first_only: bool) -> List[WebServerEntity] or WebServerEntity:
    wse = None
    query = None
    if isinstance(website_param, WebSiteEntity):
        wse = website_param
    else:
        try:
            wse = helper_web_site.get(website_param)
        except DoesNotExist:
            raise
    if first_only:
        query = WebSiteLandsAssociation.select() \
            .join_from(WebSiteLandsAssociation, WebServerEntity) \
            .where((WebSiteLandsAssociation.web_site == wse), (WebSiteLandsAssociation.https == https))\
            .limit(1)
        for row in query:
            return row.web_server
        raise DoesNotExist
    else:
        query = WebSiteLandsAssociation.select()\
            .join_from(WebSiteLandsAssociation, WebServerEntity)\
            .where((WebSiteLandsAssociation.web_site == wse), (WebSiteLandsAssociation.https == https))
        result = list()
        for row in query:
            result.append(row.web_server)
        return result
