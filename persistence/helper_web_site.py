from typing import Set
from peewee import DoesNotExist
from entities.Url import Url
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_url
from persistence.BaseModel import WebSiteEntity, WebServerEntity, WebSiteLandsAssociation


def insert(url: Url) -> WebSiteEntity:
    ue = helper_url.insert(url)
    we, created = WebSiteEntity.get_or_create(url=ue)
    return we


def get(url: Url) -> WebSiteEntity:
    try:
        ue = helper_url.get(url)
    except DoesNotExist:
        raise
    try:
        return WebSiteEntity.get(WebSiteEntity.url == ue)
    except DoesNotExist:
        raise


def get_of(wse: WebServerEntity) -> Set[WebSiteEntity]:
    query = WebSiteLandsAssociation.select()\
        .where(WebSiteLandsAssociation.web_server == wse)
    result = set()
    for row in query:
        result.add(row.web_site)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result


def get_everyone() -> Set[WebSiteEntity]:
    query = WebSiteEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result
