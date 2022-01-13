import ipaddress
from typing import Dict, Tuple, List, Set
from peewee import DoesNotExist
from entities.resolvers.IpAsDatabase import EntryIpAsDatabase
from entities.resolvers.LandingResolver import SiteLandingResult
from entities.scrapers.ROVPageScraper import RowPrefixesTable
from entities.resolvers.ScriptDependenciesResolver import MainPageScript
from entities.Zone import Zone
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from persistence import helper_web_site, helper_web_site_lands, helper_web_server, helper_zone, helper_name_server, \
    helper_zone_links, helper_domain_name_dependencies, helper_domain_name, helper_mail_domain, helper_mail_server, \
    helper_mail_domain_composed, helper_ip_address, helper_script, helper_script_withdraw, helper_script_site, \
    helper_script_hosted_on, helper_autonomous_system, helper_rov, helper_ip_network, helper_prefixes_table, \
    helper_belongs, helper_ip_address_depends, helper_access
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
            except KeyError:
                raise
            helper_domain_name_dependencies.insert(dne, ze)


def insert_mail_servers_resolving(results: Dict[str, List[str]]) -> None:
    for mail_domain in results.keys():
        mde, dne_mde = helper_mail_domain.insert(mail_domain)
        for mail_server in results[mail_domain]:
            mse, dne_mse = helper_mail_server.insert(mail_server)
            helper_mail_domain_composed.insert(mde, mse)


def insert_script_dependencies_resolving(web_site_script_dependencies: Dict[str, Tuple[Set[MainPageScript] or None, Set[MainPageScript] or None]], script_script_site_dependencies: Dict[MainPageScript, Set[str]], persist_errors=True) -> None:
    for web_site in web_site_script_dependencies.keys():
        try:
            wse = helper_web_site.get(web_site)
        except DoesNotExist:
            pass        # TODO
        https_scripts = web_site_script_dependencies[web_site][0]
        http_scripts = web_site_script_dependencies[web_site][1]

        if https_scripts is not None:
            for script in https_scripts:
                se = helper_script.insert(script.src)
                helper_script_withdraw.insert(wse, se, True, script.integrity)
                for script_site in script_script_site_dependencies[script]:
                    sse = helper_script_site.insert(script_site)
                    helper_script_hosted_on.insert(se, sse)
        else:
            if persist_errors:
                helper_script_withdraw.insert(wse, None, True, None)
            else:
                pass

        if http_scripts is not None:
            for script in http_scripts:
                se = helper_script.insert(script.src)
                helper_script_withdraw.insert(wse, se, False, script.integrity)
                for script_site in script_script_site_dependencies[script]:
                    sse = helper_script_site.insert(script_site)
                    helper_script_hosted_on.insert(se, sse)
        else:
            if persist_errors:
                helper_script_withdraw.insert(wse, None, False, None)
            else:
                pass


def insert_ip_as_and_rov_resolving(results: Dict[int, Dict[str, List[str or EntryIpAsDatabase or ipaddress.IPv4Network or RowPrefixesTable or None] or None]], persist_errors=True):
    for as_number in results.keys():
        ase = helper_autonomous_system.insert(as_number)
        for nameserver in results[as_number].keys():
            try:
                nse, dne = helper_name_server.get(nameserver)
            except DoesNotExist:
                raise
            if results[as_number][nameserver] is not None:
                ip_address = results[as_number][nameserver][0]
                entry_ip_as_db = results[as_number][nameserver][1]
                belonging_network = results[as_number][nameserver][2]
                row_prefixes_table = results[as_number][nameserver][3]

                if ip_address is not None:
                    iae = helper_ip_address.insert(ip_address)
                    if row_prefixes_table is not None:
                        re = helper_rov.insert(row_prefixes_table.rov_state.to_string(), row_prefixes_table.visibility)
                        ine = helper_ip_network.insert(row_prefixes_table.prefix)
                        helper_prefixes_table.insert(ine, re, ase)
                        helper_belongs.insert(ine, ase)
                        helper_ip_address_depends.insert(iae, ine)
                    else:
                        if belonging_network is not None:
                            ine = helper_ip_network.insert(belonging_network)
                            helper_ip_address_depends.insert(iae, ine)
                        else:
                            if persist_errors:
                                helper_ip_address_depends.insert(iae, None)
                            else:
                                pass
                else:
                    if persist_errors:
                        helper_access.insert(dne, None)
                    else:
                        pass
            else:
                pass
