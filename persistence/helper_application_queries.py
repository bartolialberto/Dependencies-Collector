from typing import Set
from peewee import DoesNotExist
from entities.Zone import Zone
from exceptions.InvalidUrlError import InvalidUrlError
from persistence import helper_web_server, helper_domain_name_dependencies, helper_script_server, helper_zone, \
    helper_domain_name, helper_web_site, helper_name_server, helper_autonomous_system, helper_web_site_domain_name
from persistence.BaseModel import ZoneEntity, WebSiteEntity, AutonomousSystemEntity
from utils import url_utils, domain_name_utils


def get_all_zone_dependencies_from_web_site(web_site: str) -> Set[ZoneEntity]:
    """
    web_site parameter could be an HTTP URL.

    """
    try:
        real_web_site = url_utils.deduct_second_component(web_site)
    except InvalidUrlError:
        raise
    zone_dependencies = set()

    # from web site domain name
    wsdna = helper_web_site_domain_name.get_from_string_web_site(real_web_site)
    web_site_dne = wsdna.domain_name
    web_site_dne_zes = helper_zone.get_zone_dependencies_of_entity_domain_name(web_site_dne)
    for ze in web_site_dne_zes:
        zone_dependencies.add(ze)

    # from web landing
    https_w_server_e = helper_web_server.get_from(real_web_site, https=True, first_only=True)
    http_w_server_e = helper_web_server.get_from(real_web_site, https=False, first_only=True)
    https_zes = helper_zone.get_zone_dependencies_of_entity_domain_name(https_w_server_e.name)
    http_zes = helper_zone.get_zone_dependencies_of_entity_domain_name(http_w_server_e.name)
    for ze in https_zes:
        zone_dependencies.add(ze)
    for ze in http_zes:
        zone_dependencies.add(ze)

    # from scripts
    s_server_es = helper_script_server.get_from_string_web_site(real_web_site)
    for sse in s_server_es:
        zes = helper_zone.get_zone_dependencies_of_entity_domain_name(sse.name)
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

    # from web site domain name
    for dne in dnes:
        try:
            wsdna = helper_web_site_domain_name.get_from_entity_domain_name(dne)
        except DoesNotExist:
            continue
        web_sites.add(wsdna.web_site)
        break       # should always be only 1

    # from scripts
    for dne in dnes:
        try:
            sse, sse_dne = helper_script_server.get(dne.string)
        except DoesNotExist:
            continue
        wses = helper_web_site.get_all_from_entity_script_server(sse)
        for wse in wses:
            web_sites.add(wse)

    # from web landing
    for dne in dnes:
        try:
            wse, wse_dne = helper_web_server.get(dne.string)
        except DoesNotExist:
            continue
        wses = helper_web_site.get_all_from_entity_web_server(wse)
        for wse in wses:
            web_sites.add(wse)

    return web_sites


def get_direct_zone_from_web_site(web_site: str) -> Zone:
    """
    web_site parameter could be an HTTP URL.

    """
    domain_name = domain_name_utils.deduct_domain_name(web_site)
    try:
        zo = helper_zone.get_direct_zone_object_of(domain_name)
    except DoesNotExist:
        raise
    return zo


def get_autonomous_systems_dependencies_from_zone_name(zone_name: str) -> Set[AutonomousSystemEntity]:
    try:
        zo = helper_zone.get_zone_object_from_zone_name(zone_name)
    except DoesNotExist:
        raise
    result = set()
    for name_server in zo.nameservers:
        try:
            nse, nse_dne = helper_name_server.get(name_server)
        except DoesNotExist:
            raise
        ases = helper_autonomous_system.get_of_entity_domain_name(nse_dne)
        result = result.union(ases)
    return result


def get_zone_names_dependencies_from_autonomous_system(as_number: int) -> Set[ZoneEntity]:
    try:
        ase = helper_autonomous_system.get(as_number)
    except DoesNotExist:
        raise
    dnes = helper_domain_name.get_all_from_entity_autonomous_system(ase)
    nses = list()
    result = set()
    for dne in dnes:
        try:
            nse, dne = helper_name_server.get(dne.string)
            nses.append(nse)
        except DoesNotExist:
            pass
    for nse in nses:
        zes = helper_zone.get_all_of_entity_name_server(nse)
        for ze in zes:
            result.add(ze)
    return result
