from typing import Dict, Set
from peewee import DoesNotExist
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from entities.resolvers.results.LandingSIteResult import LandingSiteResult
from entities.resolvers.results.MultipleDnsMailServerDependenciesResult import MultipleDnsMailServerDependenciesResult
from entities.resolvers.results.MultipleDnsZoneDependenciesResult import MultipleDnsZoneDependenciesResult
from entities.resolvers.results.ScriptDependenciesResult import ScriptDependenciesResult
from entities.resolvers.ScriptDependenciesResolver import MainPageScript
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from persistence import helper_web_site, helper_web_site_lands, helper_web_server, helper_zone, helper_name_server, \
    helper_zone_links, helper_domain_name_dependencies, helper_domain_name, helper_mail_domain, helper_mail_server, \
    helper_mail_domain_composed, helper_ip_address, helper_script, helper_script_withdraw, helper_script_site, \
    helper_script_hosted_on, helper_autonomous_system, helper_rov, helper_ip_network, helper_prefixes_table, \
    helper_belongs, helper_ip_address_depends, helper_access, helper_script_site_lands, helper_script_server


def insert_landing_web_sites_results(result: Dict[str, LandingSiteResult], persist_errors=True):
    for web_site in result.keys():
        wse = helper_web_site.insert(web_site)
        helper_web_site_lands.delete_all_from_website_entity(wse)

        # HTTPS result
        is_https = True
        if result[web_site].https is None and persist_errors == True:
            helper_web_site_lands.insert(wse, None, is_https, None)
        elif result[web_site].https is None and persist_errors == False:
            pass
        else:
            wsvr_https = helper_web_server.insert(result[web_site].https.url)
            iae = helper_ip_address.insert(result[web_site].https.ip)
            helper_web_site_lands.insert(wse, wsvr_https, is_https, iae)

        # HTTP result
        is_https = False
        if result[web_site].http is None and persist_errors == True:
            helper_web_site_lands.insert(wse, None, is_https, None)
        elif result[web_site].http is None and persist_errors == False:
            pass
        else:
            wsvr_http = helper_web_server.insert(result[web_site].http.url)
            iae = helper_ip_address.insert(result[web_site].http.ip)
            helper_web_site_lands.insert(wse, wsvr_http, is_https, iae)


def insert_dns_result(dns_results: MultipleDnsZoneDependenciesResult):
    ze_dict = dict()

    for domain_name in dns_results.zone_dependencies_per_domain_name.keys():
        try:
            dne = helper_domain_name.insert(domain_name)
        except InvalidDomainNameError:
            raise
        for zone in dns_results.zone_dependencies_per_domain_name[domain_name]:
            ze = helper_zone.insert_zone_object(zone)
            helper_domain_name_dependencies.insert(dne, ze)
            ze_dict[zone.name] = ze

    for zone_name in dns_results.zone_name_dependencies_per_zone.keys():
        try:
            ze = ze_dict[zone_name]
        except KeyError:
            raise
        for zone_dependency in dns_results.zone_name_dependencies_per_zone[zone_name]:
            try:
                ze_dep = ze_dict[zone_dependency]
            except KeyError:
                raise
            helper_zone_links.insert(ze, ze_dep)

    for name_server in dns_results.zone_name_dependencies_per_name_server.keys():
        try:
            nse, dne = helper_name_server.get(name_server)
        except DoesNotExist:
            raise
        for zone_name in dns_results.zone_name_dependencies_per_name_server[name_server]:
            try:
                ze = ze_dict[zone_name]
            except KeyError:
                raise
            helper_domain_name_dependencies.insert(dne, ze)


def insert_mail_servers_resolving(results: MultipleDnsMailServerDependenciesResult) -> None:
    for mail_domain in results.dependencies.keys():
        mde, dne_mde = helper_mail_domain.insert(mail_domain)
        for mail_server in results.dependencies[mail_domain].mail_servers:
            mse, dne_mse = helper_mail_server.insert(mail_server)
            helper_mail_domain_composed.insert(mde, mse)


def insert_script_dependencies_resolving(web_site_script_dependencies: Dict[str, ScriptDependenciesResult], script_script_site_dependencies: Dict[MainPageScript, Set[str]], persist_errors=True) -> None:
    for web_site in web_site_script_dependencies.keys():
        try:
            wse = helper_web_site.get(web_site)
        except DoesNotExist:
            raise        # TODO
        https_scripts = web_site_script_dependencies[web_site].https
        http_scripts = web_site_script_dependencies[web_site].http

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


def insert_landing_script_sites_results(result: Dict[str, LandingSiteResult], persist_errors=True):
    for script_site in result.keys():
        sse = helper_script_site.insert(script_site)
        helper_script_site_lands.delete_all_from_script_site_entity(sse)

        # HTTPS result
        is_https = True
        if result[script_site].https is None and persist_errors == True:
            helper_script_site_lands.insert(sse, None, is_https, None)
        elif result[script_site].https is None and persist_errors == False:
            pass
        else:
            sservere_https = helper_script_server.insert(result[script_site].https.url)
            iae = helper_ip_address.insert(result[script_site].https.ip)
            helper_script_site_lands.insert(sse, sservere_https, is_https, iae)

        # HTTP result
        is_https = False
        if result[script_site].http is None and persist_errors == True:
            helper_script_site_lands.insert(sse, None, is_https, None)
        elif result[script_site].http is None and persist_errors == False:
            pass
        else:
            sservere_http = helper_script_server.insert(result[script_site].http.url)
            iae = helper_ip_address.insert(result[script_site].http.ip)
            helper_script_site_lands.insert(sse, sservere_http, is_https, iae)


def insert_ip_as_and_rov_resolving(finals: ASResolverResultForROVPageScraping, persist_errors=True):
    for as_number in finals.results.keys():
        ase = helper_autonomous_system.insert(as_number)
        if finals.results[as_number] is not None:
            for nameserver in finals.results[as_number].keys():
                try:
                    nse, dne = helper_name_server.get(nameserver)
                except DoesNotExist:
                    raise
                if finals.results[as_number][nameserver] is not None:
                    ip_address = finals.results[as_number][nameserver].ip_address
                    entry_ip_as_db = finals.results[as_number][nameserver].entry_as_database
                    belonging_network = finals.results[as_number][nameserver].belonging_network
                    row_prefixes_table = finals.results[as_number][nameserver].entry_rov_page

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
        else:
            pass
