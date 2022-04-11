from typing import List, Set, Union
from peewee import DoesNotExist
from entities.SchemeUrl import SchemeUrl
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence.BaseModel import WebSiteEntity, WebSiteLandsAssociation, WebServerEntity


def insert(wsitee: WebSiteEntity, starting_https: bool, landing_url: Union[SchemeUrl, None], wservere: Union[WebServerEntity, None]) -> WebSiteLandsAssociation:
    if landing_url is None:
        if wservere is not None:
            raise ValueError
        landing_url_string = None
        landing_scheme_is_https = None
    else:
        if landing_url is None:
            raise ValueError
        if wservere.name.string != landing_url.domain_name().string:
            raise ValueError
        landing_url_string = landing_url.string
        landing_scheme_is_https = landing_url.is_https()
    wsla, created = WebSiteLandsAssociation.get_or_create(web_site=wsitee, starting_https=starting_https, landing_url=landing_url_string, web_server=wservere, landing_https=landing_scheme_is_https)
    return wsla


# insert + update = upsert
def upsert(wsitee: WebSiteEntity, starting_https: bool, landing_url: Union[SchemeUrl, None], wservere: Union[WebServerEntity, None]) -> None:
    if landing_url is None:
        if wservere is not None:
            raise ValueError
        landing_url_string = None
        landing_scheme_is_https = None
    else:
        if landing_url is None:
            raise ValueError
        if wservere.name.string != landing_url.domain_name().string:
            raise ValueError
        landing_url_string = landing_url.string
        landing_scheme_is_https = landing_url.is_https()
    WebSiteLandsAssociation.replace(web_site=wsitee, starting_https=starting_https, landing_url=landing_url_string, web_server=wservere, landing_https=landing_scheme_is_https).execute()


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


def get_all_from_entity_web_site_and_scheme(wse: WebSiteEntity, https: bool) -> List[WebSiteLandsAssociation]:
    result = list()
    query = WebSiteLandsAssociation.select()\
        .where((WebSiteLandsAssociation.web_site == wse) &
               (WebSiteLandsAssociation.https == https) &
               (WebSiteLandsAssociation.web_server.is_null(False)))
    for row in query:
        result.append(row)
    return result


def delete_unresolved_row_for(wse: WebSiteEntity, starting_https: bool) -> None:
    try:
        wsla = WebSiteLandsAssociation.get((WebSiteLandsAssociation.web_site == wse) & (WebSiteLandsAssociation.starting_https == starting_https) & (WebSiteLandsAssociation.web_server.is_null(True)))
        wsla.delete_instance()
    except DoesNotExist:
        pass


def get_unresolved() -> Set[WebSiteLandsAssociation]:
    query = WebSiteLandsAssociation.select()\
        .where(WebSiteLandsAssociation.web_server.is_null(True))
    result = set()
    for row in query:
        result.add(row)
    return result
