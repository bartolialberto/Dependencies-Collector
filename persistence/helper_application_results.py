import ipaddress
from typing import Dict, Tuple, List, Set
from peewee import DoesNotExist
from entities.IpAsDatabase import EntryIpAsDatabase
from entities.LandingResolver import SiteLandingResult
from entities.ScriptDependenciesResolver import MainPageScript
from entities.Zone import Zone
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from persistence import helper_web_site, helper_web_site_lands, helper_web_server, helper_zone, helper_name_server, \
    helper_zone_links, helper_domain_name_dependencies, helper_domain_name, helper_mail_domain, helper_mail_server, \
    helper_mail_domain_composed, helper_ip_address, helper_script, helper_script_withdraw
from utils import url_utils


def insert_landing_websites_results(result: Dict[str, Tuple[SiteLandingResult, SiteLandingResult]], persist_errors=True):
    for web_site in result.keys():
        wse = helper_web_site.insert(web_site)
        helper_web_site_lands.delete_all_from_website_entity(wse)

        # HTTPS result
        is_https = True
        https_result = result[web_site][0]
        if https_result is None and persist_errors == True:
            helper_web_site_lands.insert(wse, None, is_https, None)
        elif https_result is None and persist_errors == False:
            pass
        else:
            webserver_https = url_utils.deduct_http_url(result[web_site][0].url, as_https=is_https)
            wsvr_https = helper_web_server.insert(webserver_https)
            iae = helper_ip_address.insert(https_result.ip)
            helper_web_site_lands.insert(wse, wsvr_https, is_https, iae)

        # HTTP result
        is_https = False
        http_result = result[web_site][1]
        if http_result is None and persist_errors == True:
            helper_web_site_lands.insert(wse, None, is_https, None)
        elif http_result is None and persist_errors == False:
            pass
        else:
            webserver_http = url_utils.deduct_http_url(http_result.url, as_https=is_https)
            wsvr_http = helper_web_server.insert(webserver_http)
            iae = helper_ip_address.insert(https_result.ip)
            helper_web_site_lands.insert(wse, wsvr_http, is_https, iae)


def insert_dns_result(dns_results: Dict[str, List[Zone]], zone_dependencies_per_zone: Dict[str, List[str]], zone_names_per_nameserver: Dict[str, List[str]], persist_errors=True):
    ze_dict = dict()
    nse_dict = dict()

    for domain_name in dns_results.keys():
        try:
            dne = helper_domain_name.insert(domain_name)
        except InvalidDomainNameError:
            raise
        for zone in dns_results[domain_name]:
            ze = helper_zone.insert_zone_object(zone)
            helper_domain_name_dependencies.insert(dne, ze)
            ze_dict[zone.name] = ze

    for zone_name in zone_dependencies_per_zone.keys():
        try:
            ze = ze_dict[zone_name]
        except KeyError:
            raise
        for zone_dependency in zone_dependencies_per_zone[zone_name]:
            try:
                ze_dep = ze_dict[zone_dependency]
            except KeyError:
                raise
            helper_zone_links.insert(ze, ze_dep)

    for name_server in zone_names_per_nameserver.keys():
        try:
            nse, dne = helper_name_server.get(name_server)
        except DoesNotExist:
            raise
        for zone_name in zone_names_per_nameserver[name_server]:
            try:
                ze = ze_dict[zone_name]
            except DoesNotExist:
                raise
            helper_domain_name_dependencies.insert(dne, ze)


def insert_mail_servers_resolving(results: Dict[str, List[str]]) -> None:
    for mail_domain in results.keys():
        mde, dne_mde = helper_mail_domain.insert(mail_domain)
        for mail_server in results[mail_domain]:
            mse, dne_mse = helper_mail_server.insert(mail_server)
            helper_mail_domain_composed.insert(mde, mse)


def insert_script_dependencies_resolving(results: Dict[str, Tuple[Set[MainPageScript] or None, Set[MainPageScript] or None]], result2: Tuple[Dict[MainPageScript, Set[str]], Set[str]]) -> None:
    for web_site in results.keys():
        wse = helper_web_site.get(web_site)

        https_scripts = results[web_site][0]
        http_scripts = results[web_site][1]

        if https_scripts is not None:
            for script in https_scripts:
                se = helper_script.insert(script.src)
                helper_script_withdraw.insert(wse, se, True, script.integrity)

        if http_scripts is not None:
            for script in http_scripts:
                se = helper_script.insert(script.src)
                helper_script_withdraw.insert(wse, se, True, script.integrity)


def insert_ip_as_database_resolving(results: Dict[str, Tuple[ipaddress.IPv4Address, EntryIpAsDatabase or None, ipaddress.IPv4Network or None]]):
    pass
