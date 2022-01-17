from typing import Dict, Set
from peewee import DoesNotExist
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from entities.resolvers.results.LandingSiteResult import LandingSiteResult
from entities.resolvers.results.MultipleDnsMailServerDependenciesResult import MultipleDnsMailServerDependenciesResult
from entities.resolvers.results.MultipleDnsZoneDependenciesResult import MultipleDnsZoneDependenciesResult
from entities.resolvers.results.ScriptDependenciesResult import ScriptDependenciesResult
from entities.resolvers.ScriptDependenciesResolver import MainPageScript
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from persistence import helper_web_site, helper_web_site_lands, helper_web_server, helper_zone, helper_name_server, \
    helper_zone_links, helper_domain_name_dependencies, helper_domain_name, helper_mail_domain, helper_mail_server, \
    helper_mail_domain_composed, helper_ip_address, helper_script, helper_script_withdraw, helper_script_site, \
    helper_script_hosted_on, helper_autonomous_system, helper_rov, helper_ip_network, helper_prefixes_table, \
    helper_ip_address_depends, helper_access, helper_script_site_lands, helper_script_server, helper_ip_range_tsv, \
    helper_ip_range_rov, helper_network_numbers


def insert_all_application_results(resolvers: ApplicationResolversWrapper) -> None:
    print("[1/6] LANDING WEB SITES RESOLVING RESULTS... ", end='')
    insert_landing_web_sites_results(resolvers.landing_web_sites_results)
    print("DONE.")
    print("[2/6] DNS MAIL SERVERS DEPENDENCIES RESOLVING RESULTS... ", end='')
    insert_mail_servers_resolving(resolvers.mail_domains_results)
    print("DONE.")
    print("[3/6] DNS ZONE DEPENDENCIES RESOLVING RESULTS... ", end='')
    insert_dns_result(resolvers.total_dns_results)
    print("DONE.")
    print("[4/6] SCRIPT DEPENDENCIES RESOLVING RESULTS... ", end='')
    insert_script_dependencies_resolving(resolvers.web_site_script_dependencies, resolvers.script_script_site_dependencies)
    print("DONE.")
    print("[5/6] LANDING SCRIPT SITES RESOLVING RESULTS... ", end='')
    insert_landing_script_sites_results(resolvers.landing_script_sites_results)
    print("DONE.")
    print("[6/6] IP-AS and ROV RESOLVING RESULTS... ", end='')
    insert_ip_as_and_rov_resolving(resolvers.total_rov_page_scraper_results)
    print("DONE.")


def insert_landing_web_sites_results(result: Dict[str, LandingSiteResult]):
    for web_site in result.keys():
        w_site_e = helper_web_site.insert(web_site)
        helper_web_site_lands.delete_all_from_website_entity(w_site_e)

        # HTTPS result
        is_https = True
        if result[web_site].https is None:
            helper_web_site_lands.insert(w_site_e, None, is_https, None)
        else:
            w_server_https = helper_web_server.insert(result[web_site].https.server)
            iae = helper_ip_address.insert(result[web_site].https.ip)
            # networks and the rest is inserted in the IP-AS / ROV results later
            helper_web_site_lands.insert(w_site_e, w_server_https, is_https, iae)

        # HTTP result
        is_https = False
        if result[web_site].http is None:
            helper_web_site_lands.insert(w_site_e, None, is_https, None)
        else:
            w_server_http = helper_web_server.insert(result[web_site].http.server)
            iae = helper_ip_address.insert(result[web_site].http.ip)
            # networks and the rest is inserted in the IP-AS / ROV results later
            helper_web_site_lands.insert(w_site_e, w_server_http, is_https, iae)


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


def insert_script_dependencies_resolving(web_site_script_dependencies: Dict[str, ScriptDependenciesResult], script_script_site_dependencies: Dict[MainPageScript, Set[str]]) -> None:
    for web_site in web_site_script_dependencies.keys():
        try:
            wse = helper_web_site.get(web_site)
        except DoesNotExist:
            raise        # TODO: non dovrebbe mai succedere
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
            helper_script_withdraw.insert(wse, None, True, None)

        if http_scripts is not None:
            for script in http_scripts:
                se = helper_script.insert(script.src)
                helper_script_withdraw.insert(wse, se, False, script.integrity)
                for script_site in script_script_site_dependencies[script]:
                    sse = helper_script_site.insert(script_site)
                    helper_script_hosted_on.insert(se, sse)
        else:
            helper_script_withdraw.insert(wse, None, False, None)


def insert_landing_script_sites_results(result: Dict[str, LandingSiteResult]):
    for script_site in result.keys():
        sse = helper_script_site.insert(script_site)
        helper_script_site_lands.delete_all_from_script_site_entity(sse)

        # HTTPS result
        is_https = True
        if result[script_site].https is None:
            helper_script_site_lands.insert(sse, None, is_https, None)
        else:
            s_server_e_https = helper_script_server.insert(result[script_site].https.server)
            iae = helper_ip_address.insert(result[script_site].https.ip)
            # networks and the rest is inserted in the IP-AS / ROV results later
            helper_script_site_lands.insert(sse, s_server_e_https, is_https, iae)

        # HTTP result
        is_https = False
        if result[script_site].http is None:
            helper_script_site_lands.insert(sse, None, is_https, None)
        else:
            s_server_e_http = helper_script_server.insert(result[script_site].http.server)
            iae = helper_ip_address.insert(result[script_site].http.ip)
            # networks and the rest is inserted in the IP-AS / ROV results later
            helper_script_site_lands.insert(sse, s_server_e_http, is_https, iae)


def insert_ip_as_and_rov_resolving(finals: ASResolverResultForROVPageScraping):
    for as_number in finals.results.keys():
        ase = helper_autonomous_system.insert(as_number)
        if finals.results[as_number] is not None:
            for ip_address in finals.results[as_number].keys():
                try:
                    iae = helper_ip_address.get(ip_address)
                except DoesNotExist:
                    raise
                ine = helper_ip_network.insert_from_address_entity(iae)
                if finals.results[as_number][ip_address] is not None:
                    name_server = finals.results[as_number][ip_address].name_server
                    if name_server is not None:
                        entry_ip_as_db = finals.results[as_number][ip_address].entry_as_database
                        ip_range_tsv = finals.results[as_number][ip_address].ip_range_tsv
                        row_prefixes_table = finals.results[as_number][ip_address].entry_rov_page
                        nse, dne = helper_name_server.insert(name_server)
                        helper_access.insert(dne, iae)
                        if entry_ip_as_db is not None:
                            if ip_range_tsv is not None:
                                irte = helper_ip_range_tsv.insert(ip_range_tsv.compressed)
                                helper_network_numbers.insert(irte, ase)
                                if row_prefixes_table is not None:
                                    re = helper_rov.insert(row_prefixes_table.rov_state.to_string(), row_prefixes_table.visibility)
                                    irre = helper_ip_range_rov.insert(row_prefixes_table.prefix.compressed)
                                    helper_ip_address_depends.insert(iae, ine, irte, irre)
                                    helper_prefixes_table.insert(irre, re, ase)
                                else:
                                    helper_ip_address_depends.insert(iae, ine, irte, None)
                                    helper_prefixes_table.insert(None, None, ase)
                            else:
                                if row_prefixes_table is not None:
                                    re = helper_rov.insert(row_prefixes_table.rov_state.to_string(),
                                                           row_prefixes_table.visibility)
                                    irre = helper_ip_range_rov.insert(row_prefixes_table.prefix.compressed)
                                    helper_ip_address_depends.insert(iae, ine, None, irre)
                                    helper_prefixes_table.insert(irre, re, ase)
                                else:
                                    helper_ip_address_depends.insert(iae, ine, None, None)
                                    helper_prefixes_table.insert(None, None, ase)
                        else:
                            pass        # caso impossibile poiché non dovrebbe esserci proprio l'AS come chiave del dizionario
                    else:
                        entry_ip_as_db = finals.results[as_number][ip_address].entry_as_database
                        ip_range_tsv = finals.results[as_number][ip_address].ip_range_tsv
                        row_prefixes_table = finals.results[as_number][ip_address].entry_rov_page
                        if entry_ip_as_db is not None:
                            if ip_range_tsv is not None:
                                irte = helper_ip_range_tsv.insert(ip_range_tsv.compressed)
                                helper_network_numbers.insert(irte, ase)
                                if row_prefixes_table is not None:
                                    re = helper_rov.insert(row_prefixes_table.rov_state.to_string(),
                                                           row_prefixes_table.visibility)
                                    irre = helper_ip_range_rov.insert(row_prefixes_table.prefix.compressed)
                                    helper_ip_address_depends.insert(iae, ine, irte, irre)
                                    helper_prefixes_table.insert(irre, re, ase)
                                else:
                                    helper_ip_address_depends.insert(iae, ine, irte, None)
                                    helper_prefixes_table.insert(None, None, ase)
                            else:
                                if row_prefixes_table is not None:
                                    re = helper_rov.insert(row_prefixes_table.rov_state.to_string(),
                                                           row_prefixes_table.visibility)
                                    irre = helper_ip_range_rov.insert(row_prefixes_table.prefix.compressed)
                                    helper_ip_address_depends.insert(iae, ine, None, irre)
                                    helper_prefixes_table.insert(irre, re, ase)
                                else:
                                    helper_ip_address_depends.insert(iae, ine, None, None)
                                    helper_prefixes_table.insert(None, None, ase)
                        else:
                            pass  # caso impossibile poiché non dovrebbe esserci proprio l'AS come chiave del dizionario
                else:
                    helper_access.insert(None, iae)
                    helper_ip_address_depends.insert(iae, ine, None, None)
        else:
            pass


def dump_unresolved_entities():
    # getting web sites that didn't land
    wses = helper_web_site.get_unresolved()
