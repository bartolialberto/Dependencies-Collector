from typing import Dict, Set
from peewee import DoesNotExist
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.RRecord import RRecord
from entities.UnresolvedEntityWrapper import UnresolvedEntityWrapper
from entities.enums.ResolvingErrorCauses import ResolvingErrorCauses
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from entities.resolvers.results.LandingSiteResult import LandingSiteResult
from entities.resolvers.results.MultipleDnsMailServerDependenciesResult import MultipleDnsMailServerDependenciesResult
from entities.resolvers.results.MultipleDnsZoneDependenciesResult import MultipleDnsZoneDependenciesResult
from entities.resolvers.results.ScriptDependenciesResult import ScriptDependenciesResult
from entities.resolvers.ScriptDependenciesResolver import MainPageScript
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_web_site, helper_web_site_lands, helper_web_server, helper_zone, helper_name_server, \
    helper_zone_links, helper_domain_name_dependencies, helper_domain_name, helper_mail_domain, helper_mail_server, \
    helper_mail_domain_composed, helper_ip_address, helper_script, helper_script_withdraw, helper_script_site, \
    helper_script_hosted_on, helper_autonomous_system, helper_rov, helper_ip_network, helper_prefixes_table, \
    helper_ip_address_depends, helper_access, helper_script_site_lands, helper_script_server, helper_ip_range_tsv, \
    helper_ip_range_rov, helper_network_numbers, helper_direct_zone, helper_alias, helper_web_site_domain_name, \
    helper_script_site_domain_name
from utils import domain_name_utils


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
        w_site_dne = helper_domain_name.insert(domain_name_utils.deduct_domain_name(web_site))
        helper_web_site_domain_name.insert(w_site_e, w_site_dne)
        helper_web_site_lands.delete_all_from_entity_web_site(w_site_e)

        # HTTPS result
        is_https = True
        if result[web_site].https is None:
            helper_web_site_lands.insert(w_site_e, None, is_https)
        else:
            w_server_https, wse_https_dne = helper_web_server.insert(result[web_site].https.server)
            final_https_dne = wse_https_dne

            if len(result[web_site].https.access_path) == 0:
                pass
            elif len(result[web_site].https.access_path) == 1:
                pass
            else:
                rrs = RRecord.construct_cname_rrs_from_list_access_path(result[web_site].https.access_path)
                for rr in rrs:
                    dne = helper_domain_name.insert(rr.name)
                    alias_dne = helper_domain_name.insert(rr.get_first_value())
                    helper_alias.insert(dne, alias_dne)
                    final_https_dne = alias_dne

            for ip in result[web_site].https.ips:
                iae = helper_ip_address.insert(ip)
                helper_access.insert(final_https_dne, iae)
            # networks and the rest is inserted in the IP-AS / ROV results later
            helper_web_site_lands.insert(w_site_e, w_server_https, is_https)

        # HTTP result
        is_https = False
        if result[web_site].http is None:
            helper_web_site_lands.insert(w_site_e, None, is_https)
        else:
            w_server_http, wse_http_dne = helper_web_server.insert(result[web_site].http.server)
            final_http_dne = wse_http_dne

            if len(result[web_site].http.access_path) == 0:
                pass
            elif len(result[web_site].http.access_path) == 1:
                pass
            else:
                rrs = RRecord.construct_cname_rrs_from_list_access_path(result[web_site].http.access_path)
                for rr in rrs:
                    dne = helper_domain_name.insert(rr.name)
                    alias_dne = helper_domain_name.insert(rr.get_first_value())
                    helper_alias.insert(dne, alias_dne)
                    final_http_dne = alias_dne

            for ip in result[web_site].http.ips:
                iae = helper_ip_address.insert(ip)
                helper_access.insert(final_http_dne, iae)
            # networks and the rest is inserted in the IP-AS / ROV results later
            helper_web_site_lands.insert(w_site_e, w_server_http, is_https)


def insert_dns_result(dns_results: MultipleDnsZoneDependenciesResult):
    ze_dict = dict()    # keep the entities in a dictionary so we don't have to search them from the DB later
    dne_dict = dict()   # keep the entities in a dictionary so we don't have to search them from the DB later

    for domain_name in dns_results.zone_dependencies_per_domain_name.keys():
        try:
            dne = helper_domain_name.insert(domain_name)
        except InvalidDomainNameError:
            raise
        dne_dict[domain_name] = dne
        for zone in dns_results.zone_dependencies_per_domain_name[domain_name]:
            ze = helper_zone.insert_zone_object(zone)
            helper_domain_name_dependencies.insert(dne, ze)
            ze_dict[zone.name] = ze

    for zone_name in dns_results.zone_name_dependencies_per_zone.keys():
        try:
            ze = ze_dict[zone_name]
        except KeyError:
            ze = helper_zone.insert(zone_name)       # TODO: non dovrebbe succedere
            ze_dict[zone_name] = ze
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
            nse, dne = helper_name_server.insert(name_server)       # TODO: non dovrebbe succedere
        for zone_name in dns_results.zone_name_dependencies_per_name_server[name_server]:
            try:
                ze = ze_dict[zone_name]
            except KeyError:
                raise
            helper_domain_name_dependencies.insert(dne, ze)

    for domain_name in dns_results.direct_zone_name_per_domain_name.keys():
        dne = dne_dict[domain_name]
        if dns_results.direct_zone_name_per_domain_name[domain_name] is None:
            helper_direct_zone.insert(dne, None)
        else:
            try:
                ze = ze_dict[dns_results.direct_zone_name_per_domain_name[domain_name]]
            except KeyError:
                ze = helper_zone.insert(dns_results.direct_zone_name_per_domain_name[domain_name])      # TODO: non dovrebbe succedere
            helper_direct_zone.insert(dne, ze)


def insert_mail_servers_resolving(results: MultipleDnsMailServerDependenciesResult) -> None:
    for mail_domain in results.dependencies.keys():
        mde, dne_mde = helper_mail_domain.insert(mail_domain)
        if results.dependencies[mail_domain] is None:
            helper_mail_domain_composed.insert(mde, None)
        else:
            for mail_server in results.dependencies[mail_domain].mail_servers:
                mse, dne_mse = helper_mail_server.insert(mail_server)
                helper_mail_domain_composed.insert(mde, mse)
                try:
                    rr_a, rr_cnames = results.dependencies[mail_domain].resolve_mail_server(mail_server)
                except NoAvailablePathError:
                    helper_access.insert(dne_mse, None)
                    continue
                access_dne = mse.name
                for rr in rr_cnames:
                    prev_dne = helper_domain_name.insert(rr.name)
                    next_dne = helper_domain_name.insert(rr.get_first_value())
                    helper_alias.insert(prev_dne, next_dne)
                    access_dne = next_dne
                for value in rr_a.values:
                    iae = helper_ip_address.insert(value)
                    helper_access.insert(access_dne, iae)



def insert_script_dependencies_resolving(web_site_script_dependencies: Dict[str, ScriptDependenciesResult], script_script_site_dependencies: Dict[MainPageScript, Set[str]]) -> None:
    for web_site in web_site_script_dependencies.keys():
        try:
            wse = helper_web_site.get(web_site)
        except DoesNotExist:
            raise        # should never happen
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
        s_site_e = helper_script_site.insert(script_site)
        s_site_dne = helper_domain_name.insert(domain_name_utils.deduct_domain_name(script_site))
        helper_script_site_domain_name.insert(s_site_e, s_site_dne)
        helper_script_site_lands.delete_all_from_script_site_entity(s_site_e)   # TODO: modify

        # HTTPS result
        is_https = True
        if result[script_site].https is None:
            helper_script_site_lands.insert(s_site_e, None, is_https)
        else:
            s_server_https, sse_https_dne = helper_script_server.insert(result[script_site].https.server)
            final_https_dne = sse_https_dne

            if len(result[script_site].https.access_path) == 0:
                pass
            elif len(result[script_site].https.access_path) == 1:
                pass
            else:
                rrs = RRecord.construct_cname_rrs_from_list_access_path(result[script_site].https.access_path)
                for rr in rrs:
                    dne = helper_domain_name.insert(rr.name)
                    alias_dne = helper_domain_name.insert(rr.get_first_value())
                    helper_alias.insert(dne, alias_dne)
                    final_https_dne = alias_dne

            for ip in result[script_site].https.ips:
                iae = helper_ip_address.insert(ip)
                helper_access.insert(final_https_dne, iae)
            # networks and the rest is inserted in the IP-AS / ROV results later
            helper_script_site_lands.insert(s_site_e, s_server_https, is_https)

        # HTTP result
        is_https = False
        if result[script_site].http is None:
            helper_script_site_lands.insert(s_site_e, None, is_https)
        else:
            s_server_http, sse_http_dne = helper_script_server.insert(result[script_site].http.server)
            final_http_dne = sse_http_dne

            if len(result[script_site].http.access_path) == 0:
                pass
            elif len(result[script_site].http.access_path) == 1:
                pass
            else:
                rrs = RRecord.construct_cname_rrs_from_list_access_path(result[script_site].http.access_path)
                for rr in rrs:
                    dne = helper_domain_name.insert(rr.name)
                    alias_dne = helper_domain_name.insert(rr.get_first_value())
                    helper_alias.insert(dne, alias_dne)
                    final_http_dne = alias_dne

            for ip in result[script_site].http.ips:
                iae = helper_ip_address.insert(ip)
                helper_access.insert(final_http_dne, iae)
            # networks and the rest is inserted in the IP-AS / ROV results later
            helper_script_site_lands.insert(s_site_e, s_server_http, is_https)


def insert_ip_as_and_rov_resolving(finals: ASResolverResultForROVPageScraping):
    for as_number in finals.results.keys(): # case in which we have IP address, server, AS number, entry IP-AS, but maybe ip_range_tsv and ip_range_rov
        # START: ugly way to retrieve the AS description..
        entry_as_database = None
        for ip_address in finals.results[as_number].keys():
            entry_as_database = finals.results[as_number][ip_address].entry_as_database
            break
        # END: ugly way to retrieve the AS description..
        ase = helper_autonomous_system.insert(as_number, entry_as_database.as_description)
        for ip_address in finals.results[as_number].keys():
            try:
                iae = helper_ip_address.insert(ip_address)     # TODO: dovrebbe essere solo una get??
            except DoesNotExist:
                raise
            ine = helper_ip_network.insert_from_address_entity(iae)
            server = finals.results[as_number][ip_address].server
            ip_range_tsv = finals.results[as_number][ip_address].ip_range_tsv
            row_prefixes_table = finals.results[as_number][ip_address].entry_rov_page
            # TODO
            # dne = helper_domain_name.get(server)
            # helper_access.insert(dne, iae)
            if row_prefixes_table is not None:
                irre = helper_ip_range_rov.insert(row_prefixes_table.prefix.compressed)
                re = helper_rov.insert(row_prefixes_table.rov_state.to_string(), row_prefixes_table.visibility)
                helper_prefixes_table.insert(irre, re, ase)
                if ip_range_tsv is None:
                    helper_ip_address_depends.insert(iae, ine, None, irre)      # should not be possible...
                else:
                    irte = helper_ip_range_tsv.insert(ip_range_tsv.compressed)
                    helper_ip_address_depends.insert(iae, ine, irte, irre)
                    helper_network_numbers.insert(irte, ase)
            else:
                if ip_range_tsv is None:
                    helper_ip_address_depends.insert(iae, ine, None, None)      # should not be possible...
                else:
                    irte = helper_ip_range_tsv.insert(ip_range_tsv.compressed)
                    helper_ip_address_depends.insert(iae, ine, irte, None)
                    helper_network_numbers.insert(irte, ase)
    for ip_address in finals.no_as_results.keys():
        try:
            iae = helper_ip_address.get(ip_address)
        except DoesNotExist:
            iae = helper_ip_address.insert(ip_address)     # should never happen
        ine = helper_ip_network.insert_from_address_entity(iae)
        helper_ip_address_depends.insert(iae, ine, None, None)

    # they can be only name servers and in the insert_zone_object method invoked from the insert_dns_results, this
    # error is already persisted in the DB
    # for server in finals.unresolved_servers:
        #



def get_unresolved_entities() -> set:
    print(f"> Start retrieving all unresolved entities... ", end='')
    total_results = set()
    # getting web sites that didn't land
    https_wslas = helper_web_site_lands.get_unresolved(https=True)
    uew_https_set = UnresolvedEntityWrapper.create_from_set(https_wslas, ResolvingErrorCauses.NO_HTTPS_LANDING_FOR_WEB_SITE)
    total_results = total_results.union(uew_https_set)
    http_wslas = helper_web_site_lands.get_unresolved(https=False)
    uew_http_set = UnresolvedEntityWrapper.create_from_set(http_wslas, ResolvingErrorCauses.NO_HTTP_LANDING_FOR_WEB_SITE)
    total_results = total_results.union(uew_http_set)

    # getting IP ranges/network that didn't have a match from an IP address
    iadas = helper_ip_address_depends.get_unresolved()
    iadas_set = UnresolvedEntityWrapper.create_from_set(iadas, ResolvingErrorCauses.INCOMPLETE_DEPENDENCIES_FOR_ADDRESS)
    total_results = total_results.union(iadas_set)

    # getting script sites that didn't land
    https_sslas = helper_script_site_lands.get_https_unresolved()
    sslas_https_set = UnresolvedEntityWrapper.create_from_set(https_sslas, ResolvingErrorCauses.NO_HTTPS_LANDING_FOR_SCRIPT_SITE)
    total_results = total_results.union(sslas_https_set)
    http_sslas = helper_script_site_lands.get_http_unresolved()
    sslas_http_set = UnresolvedEntityWrapper.create_from_set(http_sslas, ResolvingErrorCauses.NO_HTTP_LANDING_FOR_SCRIPT_SITE)
    total_results = total_results.union(sslas_http_set)

    # getting name servers with no access path
    nses = helper_name_server.get_unresolved()
    nses_set = UnresolvedEntityWrapper.create_from_set(nses, ResolvingErrorCauses.NAME_SERVER_WITHOUT_ACCESS_PATH)
    total_results = total_results.union(nses_set)

    # getting script that were not possible to withdraw
    swas = helper_script_withdraw.get_unresolved()
    swas_set = UnresolvedEntityWrapper.create_from_set(swas, ResolvingErrorCauses.IMPOSSIBLE_TO_WITHDRAW_SCRIPT)
    total_results = total_results.union(swas_set)

    # getting mail domain with unresolved mail servers
    mdcas = helper_mail_domain_composed.get_unresolved()
    mdcas_set = UnresolvedEntityWrapper.create_from_set(mdcas, ResolvingErrorCauses.IMPOSSIBLE_TO_RESOLVE_MAIL_SERVERS)
    total_results = total_results.union(mdcas_set)

    # errori non gestiti??

    print(f"DONE.")
    return total_results
