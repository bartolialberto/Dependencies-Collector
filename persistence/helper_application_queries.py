from typing import Set

from peewee import DoesNotExist

from exceptions.InvalidUrlError import InvalidUrlError
from persistence import helper_web_server, helper_domain_name_dependencies, helper_script_server, helper_zone, \
    helper_domain_name, helper_web_site
from persistence.BaseModel import ZoneEntity, WebSiteEntity
from utils import url_utils


def get_all_zone_dependencies_from_web_site(web_site: str) -> Set[ZoneEntity]:
    """
    web_site parameter could be an HTTP URL.

    """
    try:
        real_web_site = url_utils.deduct_second_component(web_site)
    except InvalidUrlError:
        raise
    zone_dependencies = set()

    # from web landing
    https_w_server_e = helper_web_server.get_from(real_web_site, https=True, first_only=True)
    http_w_server_e = helper_web_server.get_from(real_web_site, https=False, first_only=True)
    https_zes = helper_domain_name_dependencies.get_all_of(https_w_server_e.name.name)
    http_zes = helper_domain_name_dependencies.get_all_of(http_w_server_e.name.name)
    for ze in https_zes:
        if ze not in zone_dependencies:
            zone_dependencies.add(ze)
    for ze in http_zes:
        if ze not in zone_dependencies:
            zone_dependencies.add(ze)

    # from scripts
    s_server_es = helper_script_server.get_from_string_web_site(real_web_site)
    for sse in s_server_es:
        zes = helper_domain_name_dependencies.get_all_of(sse.name.name)
        for ze in zone_dependencies:
            if ze not in zone_dependencies:
                zone_dependencies.add(ze)

    return zone_dependencies


def get_all_web_sites_from_zone_name(zone_name: str) -> Set[WebSiteEntity]:
    try:
        ze = helper_zone.get(zone_name)
    except DoesNotExist:
        raise
    web_sites = set()
    dnes = helper_domain_name.get_all_that_depends_on_zone(ze)

    # from scripts
    for dne in dnes:
        try:
            sse = helper_script_server.get(dne.name)
        except DoesNotExist:
            continue
        wses = helper_web_site.get_all_from_entity_script_server(sse)
        for wse in wses:
            if wse not in web_sites:
                web_sites.add(wse)

    # from web landing
    for dne in dnes:
        try:
            wse = helper_web_server.get(dne.name)
        except DoesNotExist:
            continue
        wses = helper_web_site.get_all_from_entity_web_server(wse)
        for wse in wses:
            if wse not in web_sites:
                web_sites.add(wse)

    return web_sites
