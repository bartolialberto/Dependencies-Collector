from typing import Set, Tuple
from peewee import DoesNotExist
from entities.DomainName import DomainName
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_domain_name
from persistence.BaseModel import WebServerEntity, WebSiteEntity, WebSiteLandsAssociation, DomainNameEntity


def insert(name: DomainName) -> WebServerEntity:
    dne = helper_domain_name.insert(name)
    wse, created = WebServerEntity.get_or_create(name=dne)
    return wse


def get(name: DomainName) -> WebServerEntity:
    try:
        dne = helper_domain_name.get(name)
    except DoesNotExist:
        raise
    try:
        wse = WebServerEntity.get(WebServerEntity.name == dne)
    except DoesNotExist:
        raise
    return wse


def get_of(wse: WebSiteEntity, starting_https: bool) -> WebServerEntity:
    try:
        wsla = WebSiteLandsAssociation.get((WebSiteLandsAssociation.web_site == wse) & (WebSiteLandsAssociation.starting_https == starting_https))
        return wsla.web_server
    except DoesNotExist:
        raise


def get_from(wse: WebSiteEntity) -> Tuple[WebServerEntity, WebServerEntity]:
    https_web_server = None
    http_web_server = None

    query = WebSiteLandsAssociation.select()\
        .where(WebSiteLandsAssociation.web_site == wse)
    result = set()
    for row in query:
        if row.starting_https:
            result.add(row.web_server)
            https_web_server = row.web_server
        else:
            result.add(row.web_server)
            http_web_server = row.web_server
    if len(result) == 1:
        return https_web_server, http_web_server
    elif len(result) == 2:
        return https_web_server, http_web_server
    else:
        raise NoDisposableRowsError


def filter_domain_names(dnes: Set[DomainNameEntity]) -> Set[WebServerEntity]:
    query = WebServerEntity.select()\
        .where(WebServerEntity.name.in_(dnes))
    result = set()
    for row in query:
        result.add(row)
    if len(result) == 0:
        raise NoDisposableRowsError
    else:
        return result


def get_everyone() -> Set[WebServerEntity]:
    query = WebServerEntity.select()
    result = set()
    for row in query:
        result.add(row)
    return result
