from typing import Set
from peewee import DoesNotExist
from entities.Zone import Zone
from persistence import helper_web_server, helper_script_server, helper_zone, helper_domain_name, helper_web_site, \
    helper_name_server, helper_autonomous_system, helper_web_site_domain_name, helper_mail_domain, helper_mail_server, \
    helper_script_site
from persistence.BaseModel import ZoneEntity, WebSiteEntity, AutonomousSystemEntity, MailDomainEntity
from utils import domain_name_utils


def get_all_zone_dependencies_from_web_site(wse: WebSiteEntity, from_script_sites=False) -> Set[ZoneEntity]:
    zone_dependencies = set()

    # from web site domain name
    wsdna = helper_web_site_domain_name.get_from_entity_web_site(wse)
    web_site_dne = wsdna.domain_name
    web_site_dne_zes = helper_zone.get_zone_dependencies_of_entity_domain_name(web_site_dne)
    for ze in web_site_dne_zes:
        zone_dependencies.add(ze)

    # from web landing
    w_server_es = helper_web_server.get_from_entity_web_site(wse)       # HTTPS and HTTP
    for w_server_e in w_server_es:
        zes = helper_zone.get_zone_dependencies_of_entity_domain_name(w_server_e)
        for ze in zes:
            zone_dependencies.add(ze)

    if from_script_sites:
        # from scripts
        s_site_es = helper_script_site.get_from_entity_web_site(wse)
        s_site_dnes = set(map(lambda s_site_e: s_site_e.domain_name, s_site_es))
        for s_site_dne in s_site_dnes:
            zes = helper_zone.get_zone_dependencies_of_entity_domain_name(s_site_dne)
            for ze in zes:
                zone_dependencies.add(ze)
        for s_site_e in s_site_es:
            s_server_es = helper_script_server.get_from_entity_script_site(s_site_e)
            for sse in s_server_es:
                zes = helper_zone.get_zone_dependencies_of_entity_domain_name(sse.name)
                for ze in zes:
                    zone_dependencies.add(ze)

    return zone_dependencies


def get_all_direct_zones_from_web_site(web_site: str) -> Set[ZoneEntity]:
    try:
        wse = helper_web_site.get(web_site)
    except DoesNotExist:
        raise
    direct_zones = set()

    # from web site domain name
    wsdna = helper_web_site_domain_name.get_from_entity_web_site(wse)
    web_site_dne = wsdna.domain_name
    web_site_dne_direct_ze = helper_zone.get_direct_zone_of(web_site_dne)
    direct_zones.add(web_site_dne_direct_ze)

    # from web landing
    https_w_server_e = helper_web_server.get_from_web_site_and_scheme(wse, https=True, first_only=True)
    http_w_server_e = helper_web_server.get_from_web_site_and_scheme(wse, https=False, first_only=True)
    https_direct_ze = helper_zone.get_direct_zone_of(https_w_server_e._second_component_)
    http_direct_ze = helper_zone.get_direct_zone_of(http_w_server_e._second_component_)
    direct_zones.add(https_direct_ze)
    direct_zones.add(http_direct_ze)

    # from scripts
    s_server_es = helper_script_server.get_from_entity_web_site(wse)
    for sse in s_server_es:
        zes = helper_zone.get_zone_dependencies_of_entity_domain_name(sse.name)
        for ze in zes:
            direct_zones.add(ze)

    return direct_zones


def get_all_zone_dependencies_from_mail_domain(mde: MailDomainEntity) -> Set[ZoneEntity]:
    zone_dependencies = set()

    # from mail domain name
    mail_domain_dne_zes = helper_zone.get_zone_dependencies_of_entity_domain_name(mde.name)
    for ze in mail_domain_dne_zes:
        zone_dependencies.add(ze)

    # from mail servers
    mses = helper_mail_server.get_every_of(mde)
    for mse in mses:
        zes = helper_zone.get_zone_dependencies_of_entity_domain_name(mse.name)
        for ze in zes:
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
            wsdnas = helper_web_site_domain_name.get_from_entity_domain_name(dne)
        except DoesNotExist:
            continue
        for wsdna in wsdnas:
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
