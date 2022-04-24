import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Set
from peewee import DoesNotExist
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.DomainName import DomainName
from entities.Url import Url
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from entities.resolvers.results.LandingSiteResult import LandingSiteResult
from entities.resolvers.results.MultipleMailDomainResolvingResult import MultipleMailDomainResolvingResult
from entities.resolvers.results.MultipleDnsZoneDependenciesResult import MultipleDnsZoneDependenciesResult
from entities.resolvers.results.ScriptDependenciesResult import ScriptDependenciesResult
from entities.MainFrameScript import MainFrameScript
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from persistence import helper_web_site, helper_web_site_lands, helper_web_server, helper_zone, helper_name_server, \
    helper_zone_links, helper_domain_name_dependencies, helper_domain_name, helper_mail_domain, helper_mail_server, \
    helper_mail_domain_composed, helper_ip_address, helper_script, helper_script_withdraw, helper_script_site, \
    helper_script_hosted_on, helper_autonomous_system, helper_rov, helper_ip_network, helper_prefixes_table, \
    helper_ip_address_depends, helper_access, helper_script_site_lands, helper_script_server, helper_ip_range_tsv, \
    helper_ip_range_rov, helper_network_numbers, helper_direct_zone, helper_web_site_domain_name, \
    helper_script_site_domain_name, helper_paths
from persistence.BaseModel import db, MailDomainComposedAssociation, WebSiteLandsAssociation, ScriptWithdrawAssociation, \
    ScriptSiteLandsAssociation, AccessAssociation, IpAddressDependsAssociation
from static_variables import OUTPUT_FOLDER_NAME
from utils import datetime_utils, file_utils, csv_utils, string_utils


# dict to save entities' objects and share them between methods, avoiding searching such entities in the DB
domain_name_dict = dict()
zone_dict = dict()
web_site_dict = dict()
url_dict = dict()


def insert_all_application_results(resolvers: ApplicationResolversWrapper) -> None:
    start_execution_time = datetime.now()
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
    print(f"All insertions took in total: ({datetime_utils.compute_delta_and_stamp(start_execution_time)})")


def insert_landing_web_sites_results(result: Dict[Url, LandingSiteResult]):
    with db.atomic():       # peewee transaction
        for web_site in result.keys():
            w_site_e = helper_web_site.insert(web_site)
            w_site_dne = helper_domain_name.insert(web_site.domain_name())
            helper_web_site_domain_name.insert(w_site_e, w_site_dne)

            # helper_web_site_lands.delete_all_from_entity_web_site(w_site_e)
            #
            url_dict[web_site] = w_site_e.url
            web_site_dict[web_site] = w_site_e
            domain_name_dict[web_site.domain_name()] = w_site_dne

            # HTTPS result
            is_starting_scheme_https = True
            if result[web_site].https is None:
                helper_web_site_lands.upsert(w_site_e, is_starting_scheme_https, None, None)
            else:
                w_server_https = helper_web_server.insert(result[web_site].https.server)
                helper_paths.insert_a_path(result[web_site].https.a_path)
                # networks and the rest is inserted in the IP-AS / ROV results later
                helper_web_site_lands.delete_unresolved_row_for(w_site_e, is_starting_scheme_https)
                helper_web_site_lands.upsert(w_site_e, is_starting_scheme_https, result[web_site].https.url, w_server_https)

            # HTTP result
            is_starting_scheme_https = False
            if result[web_site].http is None:
                helper_web_site_lands.upsert(w_site_e, is_starting_scheme_https, None, None)
            else:
                w_server_http = helper_web_server.insert(result[web_site].http.server)
                helper_paths.insert_a_path(result[web_site].http.a_path)
                # networks and the rest is inserted in the IP-AS / ROV results later
                helper_web_site_lands.delete_unresolved_row_for(w_site_e, is_starting_scheme_https)
                helper_web_site_lands.upsert(w_site_e, is_starting_scheme_https, result[web_site].http.url, w_server_http)


def insert_dns_result(dns_results: MultipleDnsZoneDependenciesResult):
    dependencies_data_source = list()
    key_dependencies_dne = 'domain_name'
    key_dependencies_ze = 'zone'
    direct_zones_data_source = list()
    key_direct_zones_dne = 'domain_name'
    key_direct_zones_ze = 'zone'
    with db.atomic():       # peewee transaction
        # all zone dataset
        for domain_name in dns_results.zone_dependencies_per_domain_name.keys():
            try:
                dne = domain_name_dict[domain_name]
            except KeyError:
                try:
                    dne = helper_domain_name.insert(domain_name)
                    domain_name_dict[domain_name] = dne
                except InvalidDomainNameError:
                    raise
            for zone in dns_results.zone_dependencies_per_domain_name[domain_name]:
                try:
                    ze = zone_dict[zone.name]
                except KeyError:
                    ze = helper_zone.insert_zone_object(zone)
                    zone_dict[zone.name] = ze
                dependencies_data_source.append({key_dependencies_dne: dne, key_dependencies_ze: ze})

        for zone in dns_results.zone_dependencies_per_zone.keys():
            try:
                ze = zone_dict[zone.name]
            except KeyError:
                ze = helper_zone.insert(zone.name)
                zone_dict[zone.name] = ze
            for zone_dependency in dns_results.zone_dependencies_per_zone[zone]:
                try:
                    ze_dep = zone_dict[zone_dependency.name]
                except KeyError:
                    ze_dep = helper_zone.insert(zone.name)
                    zone_dict[zone.name] = ze_dep
                helper_zone_links.insert(ze, ze_dep)

        for name_server in dns_results.zone_dependencies_per_name_server.keys():
            try:
                nse_dne = domain_name_dict[name_server]
            except KeyError:
                try:
                    nse = helper_name_server.get(name_server)
                except DoesNotExist:
                    nse = helper_name_server.insert(name_server)       # TODO: non dovrebbe succedere
                nse_dne = nse.name

            for zone in dns_results.zone_dependencies_per_name_server[name_server]:
                try:
                    ze_dep = zone_dict[zone.name]
                except KeyError:
                    ze_dep = helper_zone.insert(zone.name)
                    zone_dict[zone.name] = ze_dep
                dependencies_data_source.append({key_dependencies_dne: nse_dne, key_dependencies_ze: ze_dep})

        for domain_name in dns_results.direct_zones.keys():
            try:
                dne = domain_name_dict[domain_name]
            except KeyError:
                dne = helper_domain_name.insert(domain_name)
            if dns_results.direct_zones[domain_name] is None:
                # helper_direct_zone.insert(dne, None)
                direct_zones_data_source.append({key_direct_zones_dne: dne, key_direct_zones_ze: None})
            else:
                try:
                    direct_ze = zone_dict[dns_results.direct_zones[domain_name].name]
                except KeyError:
                    direct_ze = helper_zone.get(dns_results.direct_zones[domain_name].name)
                # helper_direct_zone.insert(dne, direct_ze)
                direct_zones_data_source.append({key_direct_zones_dne: dne, key_direct_zones_ze: direct_ze})

    with db.atomic():  # peewee transaction
        helper_domain_name_dependencies.bulk_upserts(dependencies_data_source)
        helper_direct_zone.bulk_upserts(direct_zones_data_source)


def insert_mail_servers_resolving(results: MultipleMailDomainResolvingResult) -> None:
    data_source = list()
    key_mde = 'mail_domain'
    key_mse = 'mail_server'
    with db.atomic():  # peewee transaction
        for mail_domain in results.dependencies.keys():
            mde = helper_mail_domain.insert(mail_domain)
            if results.dependencies[mail_domain] is None:
                data_source.append({key_mde: mde, key_mse: None})
            else:
                for mail_server in results.dependencies[mail_domain].mail_servers_paths.keys():
                    if results.dependencies[mail_domain].mail_servers_paths[mail_server] is None:
                        mse = helper_mail_server.insert(mail_server)
                        data_source.append({key_mde: mde, key_mse: None})
                        helper_access.insert(mse.name, None)

                        #
                        domain_name_dict[DomainName(mse.name.string)] = mse.name
                    else:
                        mse, dnes, ipes = helper_paths.insert_a_path_for_mail_servers(results.dependencies[mail_domain].mail_servers_paths[mail_server], mde)

                        #
                        domain_name_dict[DomainName(mse.name.string)] = mse.name
                        for dne in dnes:
                            domain_name_dict[DomainName(dne.string)] = dne
            #
            domain_name_dict[mail_domain] = mde.name

    with db.atomic():  # peewee transaction
        helper_mail_domain_composed.bulk_upserts(data_source)


def insert_script_dependencies_resolving(web_site_script_dependencies: Dict[Url, ScriptDependenciesResult], script_script_site_dependencies: Dict[MainFrameScript, Set[Url]]) -> None:
    with db.atomic():  # peewee transaction
        for web_site in web_site_script_dependencies.keys():
            try:
                wse = web_site_dict[web_site]
            except KeyError:
                try:
                    wse = helper_web_site.get(web_site)
                    web_site_dict[web_site] = wse
                except DoesNotExist:
                    raise        # should never happen
            https_scripts = web_site_script_dependencies[web_site].https
            http_scripts = web_site_script_dependencies[web_site].http

            # HTTPS
            is_https = True
            if https_scripts is not None:
                helper_script_withdraw.delete_unresolved_row_for(wse, is_https)
                for script in https_scripts:
                    se = helper_script.insert(script.src)
                    helper_script_withdraw.insert(wse, se, is_https, script.integrity)
                    for script_site in script_script_site_dependencies[script]:
                        sse = helper_script_site.insert(script_site)
                        helper_script_hosted_on.insert(se, sse)
            else:
                helper_script_withdraw.insert(wse, None, is_https, None)

            # HTTP
            is_https = False
            if http_scripts is not None:
                helper_script_withdraw.delete_unresolved_row_for(wse, is_https)
                for script in http_scripts:
                    se = helper_script.insert(script.src)
                    helper_script_withdraw.insert(wse, se, is_https, script.integrity)
                    for script_site in script_script_site_dependencies[script]:
                        sse = helper_script_site.insert(script_site)
                        helper_script_hosted_on.insert(se, sse)
            else:
                helper_script_withdraw.insert(wse, None, is_https, None)


def insert_landing_script_sites_results(result: Dict[Url, LandingSiteResult]):
    with db.atomic():  # peewee transaction
        for script_site in result.keys():
            s_site_e = helper_script_site.insert(script_site)
            s_site_dne = helper_domain_name.insert(script_site.domain_name())
            helper_script_site_domain_name.insert(s_site_e, s_site_dne)

            # HTTPS result
            is_starting_scheme_https = True
            if result[script_site].https is None:
                helper_script_site_lands.upsert(s_site_e, is_starting_scheme_https, None, None)
            else:
                s_server_https = helper_script_server.insert(result[script_site].https.server)
                helper_paths.insert_a_path(result[script_site].https.a_path)
                # networks and the rest is inserted in the IP-AS / ROV results later
                helper_script_site_lands.delete_unresolved_row_for(s_site_e, is_starting_scheme_https)
                helper_script_site_lands.upsert(s_site_e, is_starting_scheme_https, result[script_site].https.url, s_server_https)

            # HTTP result
            is_starting_scheme_https = False
            if result[script_site].http is None:
                helper_script_site_lands.upsert(s_site_e, is_starting_scheme_https, None, None)
            else:
                s_server_http = helper_script_server.insert(result[script_site].http.server)
                helper_paths.insert_a_path(result[script_site].http.a_path)
                # networks and the rest is inserted in the IP-AS / ROV results later
                helper_script_site_lands.delete_unresolved_row_for(s_site_e, is_starting_scheme_https)
                helper_script_site_lands.upsert(s_site_e, is_starting_scheme_https, result[script_site].http.url, s_server_http)


def insert_ip_as_and_rov_resolving(finals: ASResolverResultForROVPageScraping):
    data_source = list()
    key_iae = 'ip_address'
    key_ine = 'ip_network'
    key_irte = 'ip_range_tsv'
    key_irre = 'ip_range_rov'
    with db.atomic():       # peewee transaction
        for as_number in finals.results.keys(): # case in which we have IP address, server, AS number, entry IP-AS, but maybe ip_range_tsv and ip_range_rov
            for ip_address in finals.results[as_number].keys():
                entry_as_database = finals.results[as_number][ip_address].entry_as_database
                ase = helper_autonomous_system.insert(entry_as_database)
                iae = helper_ip_address.insert(ip_address)
                ine = helper_ip_network.insert_from_address_entity(iae)
                # server = finals.results[as_number][ip_address].server
                ip_range_tsv = finals.results[as_number][ip_address].ip_range_tsv
                row_prefixes_table = finals.results[as_number][ip_address].entry_rov_page
                if row_prefixes_table is not None:
                    irre = helper_ip_range_rov.insert(row_prefixes_table.prefix)
                    # re = helper_rov.insert(row_prefixes_table.rov_state.to_string(), row_prefixes_table.visibility)
                    re = helper_rov.insert(row_prefixes_table)
                    helper_prefixes_table.insert(irre, re, ase)
                    if ip_range_tsv is None:
                        # helper_ip_address_depends.insert(iae, ine, None, irre)      # should not be possible...
                        data_source.append({key_iae: iae, key_ine: ine, key_irte: None, key_irre: irre})
                    else:
                        irte = helper_ip_range_tsv.insert(ip_range_tsv.compressed)
                        # helper_ip_address_depends.insert(iae, ine, irte, irre)
                        data_source.append({key_iae: iae, key_ine: ine, key_irte: irte, key_irre: irre})
                        helper_network_numbers.insert(irte, ase)
                else:
                    if ip_range_tsv is None:
                        # helper_ip_address_depends.insert(iae, ine, None, None)      # should not be possible...
                        data_source.append({key_iae: iae, key_ine: ine, key_irte: None, key_irre: None})
                    else:
                        irte = helper_ip_range_tsv.insert(ip_range_tsv.compressed)
                        # helper_ip_address_depends.insert(iae, ine, irte, None)
                        data_source.append({key_iae: iae, key_ine: ine, key_irte: irte, key_irre: None})
                        helper_network_numbers.insert(irte, ase)
        for ip_address in finals.no_as_results.keys():
            iae = helper_ip_address.insert(ip_address)     # should never happen
            ine = helper_ip_network.insert_from_address_entity(iae)
            # helper_ip_address_depends.insert(iae, ine, None, None)
            data_source.append({key_iae: iae, key_ine: ine, key_irte: None, key_irre: None})

    with db.atomic():  # peewee transaction
        helper_ip_address_depends.bulk_upserts(data_source)

        # they can be only name servers and in the insert_zone_object method invoked from the insert_dns_results, this
        # error is already persisted in the DB
        # for server in finals.unresolved_servers:
            #


def get_unresolved_entities(execute_rov_scraping=True) -> set:
    print(f"> Start retrieving all unresolved entities... ", end='')
    total_results = set()

    with db.atomic():       # peewee transaction
        # getting web sites that didn't land: WebSiteLandsAssociation
        unresolved_web_site_lands_association = helper_web_site_lands.get_unresolved()
        total_results = total_results.union(unresolved_web_site_lands_association)

        # getting script that were not possible to withdraw: ScriptWithdrawAssociation
        script_withdraw_associations_incomplete = helper_script_withdraw.get_unresolved()
        total_results = total_results.union(script_withdraw_associations_incomplete)

        # getting script sites that didn't land: ScriptSiteLandsAssociation
        unresolved_script_site_lands_association = helper_script_site_lands.get_unresolved()
        total_results = total_results.union(unresolved_script_site_lands_association)

        # getting domain names with no access path: AccessAssociation
        domain_name_with_no_access_path = helper_access.get_unresolved()
        total_results = total_results.union(domain_name_with_no_access_path)

        # getting unresolved mail domain: MailDomainComposedAssociation
        mdcas = helper_mail_domain_composed.get_unresolved()
        total_results = total_results.union(mdcas)

        if execute_rov_scraping:
            # getting IP ranges/network that didn't have a match from an IP address: IpAddressDependsAssociation
            ip_address_depends_associations_incomplete = helper_ip_address_depends.get_unresolved(execute_rov_scraping)
            total_results = total_results.union(ip_address_depends_associations_incomplete)

    print(f"DONE.")
    return total_results


def dump_all_unresolved_entities(project_root_folder=Path.cwd(), separator=';', unresolved_entities=None, execute_rov_scraping=True) -> None:
    if unresolved_entities is None:
        unresolved_entities = get_unresolved_entities(execute_rov_scraping)
    else:
        if isinstance(unresolved_entities, set):
            pass
        else:
            raise ValueError
    file = file_utils.set_file_in_folder(OUTPUT_FOLDER_NAME, 'unresolved_entities.csv', project_root_folder)
    with file.open('w', encoding='utf-8', newline='') as f:
        write = csv.writer(f, dialect=csv_utils.return_personalized_dialect_name(f"{separator}"))
        write.writerow(['table_name', 'class_type', 'reason_phrase'])
        for unresolved_entity in unresolved_entities:
            to_be_written = list()
            if isinstance(unresolved_entity, WebSiteLandsAssociation):
                to_be_written.append(WebSiteLandsAssociation._meta.table_name)
                to_be_written.append(WebSiteLandsAssociation.__name__)
                to_be_written.append(f"Web site: {unresolved_entity.web_site.url.string} with starting scheme: {string_utils.stamp_https_from_bool(unresolved_entity.starting_https)} can't land")
            elif isinstance(unresolved_entity, ScriptWithdrawAssociation):
                to_be_written.append(ScriptWithdrawAssociation._meta.table_name)
                to_be_written.append(ScriptWithdrawAssociation.__name__)
                to_be_written.append(f"Can't resolve scripts of web site: {unresolved_entity.web_site.url.string} on scheme: {string_utils.stamp_https_from_bool(unresolved_entity.https)}")
            elif isinstance(unresolved_entity, ScriptSiteLandsAssociation):
                to_be_written.append(ScriptSiteLandsAssociation._meta.table_name)
                to_be_written.append(ScriptSiteLandsAssociation.__name__)
                to_be_written.append(f"Script site: {unresolved_entity.script_site.url.string} with starting scheme: {string_utils.stamp_https_from_bool(unresolved_entity.starting_https)} can't land")
            elif isinstance(unresolved_entity, AccessAssociation):
                to_be_written.append(AccessAssociation._meta.table_name)
                to_be_written.append(AccessAssociation.__name__)
                to_be_written.append(f"Can't resolve an A type RR of domain name: {unresolved_entity.domain_name.string}")
            elif isinstance(unresolved_entity, MailDomainComposedAssociation):
                to_be_written.append(MailDomainComposedAssociation._meta.table_name)
                to_be_written.append(MailDomainComposedAssociation.__name__)
                to_be_written.append(f"Can't resolve a MX type RR of mail domain: {unresolved_entity.mail_domain.name.string}")
            elif isinstance(unresolved_entity, IpAddressDependsAssociation):
                to_be_written.append(IpAddressDependsAssociation._meta.table_name)
                to_be_written.append(IpAddressDependsAssociation.__name__)
                if unresolved_entity.ip_range_tsv is None and unresolved_entity.ip_range_rov is None:
                    to_be_written.append(f"IP address: {unresolved_entity.ip_address.exploded_notation} has both IP range unresolved")
                elif unresolved_entity.ip_range_tsv is None and unresolved_entity.ip_range_rov is not None:
                    to_be_written.append(f"IP address: {unresolved_entity.ip_address.exploded_notation} has IP range TSV unresolved")
                elif unresolved_entity.ip_range_tsv is not None and unresolved_entity.ip_range_rov is None:
                    to_be_written.append(f"IP address: {unresolved_entity.ip_address.exploded_notation} has IP range ROV unresolved")
                else:
                    raise ValueError
            else:
                raise ValueError
            write.writerow(to_be_written)
        f.close()
