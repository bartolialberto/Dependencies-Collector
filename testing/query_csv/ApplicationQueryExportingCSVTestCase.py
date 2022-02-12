import csv
import ipaddress
import unittest
from pathlib import Path
from typing import List
from peewee import DoesNotExist
from entities.Zone import Zone
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_web_server, helper_zone, helper_web_site, helper_domain_name, helper_mail_domain, \
    helper_mail_server, helper_name_server, helper_autonomous_system, helper_ip_network, helper_application_queries, \
    helper_ip_address, helper_web_site_domain_name
from persistence.BaseModel import IpNetworkEntity
from utils import file_utils, csv_utils, network_utils


class ApplicationQueryExportingCSVTestCase(unittest.TestCase):
    @staticmethod
    def write_csv_file(file: Path, separator: str, rows: List[List[str]]) -> None:
        try:
            with file.open('w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, dialect=f'{csv_utils.return_personalized_dialect_name(separator)}')
                for row in rows:
                    writer.writerow(row)
                f.close()
        except PermissionError:
            raise
        except FileNotFoundError:
            raise
        except OSError:
            raise

    @staticmethod
    def are_all_name_servers_of_zone_object_in_network(zo: Zone, network_param: IpNetworkEntity) -> bool:
        network = ipaddress.IPv4Network(network_param.compressed_notation)
        all_addresses = set()
        for name_server in zo.nameservers:
            try:
                rr_a = zo.resolve_name_server_access_path(name_server)
            except NoAvailablePathError:
                raise
            for value in rr_a.values:
                all_addresses.add(ipaddress.IPv4Address(value))
        for address in all_addresses:
            if network_utils.is_in_network(address, network):
                pass
            else:
                return False
        return True

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.sub_folder = 'output'
        cls.separator = ','

    def test_1_query_number_of_dependencies_of_all_zones(self):
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF ZONE NAME")
        # PARAMETER
        zes = helper_zone.get_everyone()
        # this flag tells if we have to export a zone name that we know it is a zone (NS RR was resolved) but each
        # nameserver's A RR was not resolved. In that case the zone row will be added and for each field regarding the
        # relative infos will present the string value: ND
        only_complete_zones = False
        unresolved_value = 'ND'
        filename = 'zone_infos'
        # QUERY
        print(f"Parameters: {len(zes)} zones retrieved from database.")
        rows = list()
        rows.append(["zone_name", "#nameservers", "#networks", "#as"])
        count_complete_zones = 0
        count_incomplete_zones = 0
        for ze in zes:
            try:
                nses = helper_name_server.get_all_from_zone_entity(ze)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            ases = set()
            iaes = set()
            ines = set()
            is_unresolved = False
            for nse in nses:
                try:
                    nse_iaes, path_dnes = helper_domain_name.resolve_access_path(nse.name, get_only_first_address=False)
                except (DoesNotExist, NoAvailablePathError):
                    is_unresolved = True
                    break
                for iae in nse_iaes:
                    iaes.add(iae)
                    try:
                        ine = helper_ip_network.get_of(iae)
                    except (DoesNotExist, NoAvailablePathError):
                        raise
                    ines.add(ine)
                    try:
                        ase = helper_autonomous_system.get_of_entity_ip_address(iae)
                    except DoesNotExist:
                        print('')
                        continue        # TODO
                    ases.add(ase)
            if not only_complete_zones and is_unresolved:
                rows.append([ze.name, unresolved_value, unresolved_value, unresolved_value])
                count_incomplete_zones = count_incomplete_zones + 1
            else:
                rows.append([ze.name, str(len(iaes)), str(len(ines)), str(len(ases))])
                count_complete_zones = count_complete_zones + 1
            if len(ases) > len(ines):
                print(f"ERROR: {ze.name} has more ases {len(ases)} than ines {len(ines)}")
        print(f"Written {len(rows)} rows.")
        if not only_complete_zones:
            print(f"---> {count_complete_zones} complete zones.")
            print(f"---> {count_incomplete_zones} incomplete zones.")

        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_2_query_direct_zones_from_all_web_sites(self):
        print(f"--- QUERY DIRECT ZONES FROM WEB SITES AND ASSOCIATED WEB SERVERS")
        # PARAMETER
        wses = helper_web_site.get_everyone()
        filename = 'web_sites_direct_zone_dependencies'
        # QUERY
        print(f"Parameters: {len(wses)} web sites retrieved from database.")
        rows = list()
        rows.append(['web_site', 'zone_name'])
        for wse in wses:
            w_server_es = helper_web_server.get_from_entity_web_site(wse)
            try:
                web_site_dne = helper_domain_name.get_from_entity_web_site(wse)
            except DoesNotExist as e:
                raise
            zone_name_dependencies_of_wse = set()
            try:
                web_site_direct_zone = helper_zone.get_direct_zone_of(web_site_dne)
                web_site_direct_zone_name = web_site_direct_zone.name
                zone_name_dependencies_of_wse.add(web_site_direct_zone_name)
            except DoesNotExist:
                pass                  # could be a TLD that are not considered
            for w_server_e in w_server_es:
                try:
                    web_server_direct_zone = helper_zone.get_direct_zone_of(w_server_e.name)
                    web_server_direct_zone_name = web_server_direct_zone.name
                    zone_name_dependencies_of_wse.add(web_server_direct_zone_name)
                except DoesNotExist:
                    pass          # could be a TLD that are not considered
            for zone_name in zone_name_dependencies_of_wse:
                rows.append([wse.url.string, zone_name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_3_query_direct_zones_from_all_mail_domains(self):
        print(f"--- QUERY DIRECT ZONES FROM MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        # PARAMETER
        mdes = helper_mail_domain.get_everyone()
        filename = 'mail_domains_direct_zone_dependencies'
        # QUERY
        print(f"Parameters: {len(mdes)} mail domains retrieved from database.")
        rows = list()
        rows.append(['mail_domain', 'zone_name'])
        for mde in mdes:
            mail_domain_dne = mde.name
            try:
                mses = helper_mail_server.get_every_of(mde)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            zone_name_dependencies_of_mde = set()
            try:
                mail_domain_direct_zone = helper_zone.get_direct_zone_of(mail_domain_dne)
                mail_domain_direct_zone_name = mail_domain_direct_zone.name
                zone_name_dependencies_of_mde.add(mail_domain_direct_zone_name)
            except DoesNotExist:
                pass        # could be a TLD that are not considered
            for mse in mses:
                try:
                    mail_server_server_direct_zone = helper_zone.get_direct_zone_of(mse.name)
                except DoesNotExist:
                    continue
                mail_server_server_direct_zone_name = mail_server_server_direct_zone.name
                zone_name_dependencies_of_mde.add(mail_server_server_direct_zone_name)
            for zone_name in zone_name_dependencies_of_mde:
                rows.append([mde.name.string, zone_name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_4_query_zones_from_all_web_sites(self):
        print(f"--- QUERY ZONES FROM WEB SITES AND ASSOCIATED WEB SERVERS")
        # PARAMETER
        wses = helper_web_site.get_everyone()
        filename = 'web_sites_zone_dependencies'
        # QUERY
        print(f"Parameters: {len(wses)} web sites retrieved from database.")
        rows = list()
        rows.append(['web_site', 'zone_name'])
        for wse in wses:
            w_server_es = helper_web_server.get_from_entity_web_site(wse)
            try:
                web_site_dne = helper_domain_name.get_from_entity_web_site(wse)
            except DoesNotExist as e:
                continue
            zone_name_dependencies_of_wse = set()
            try:
                web_site_direct_zones = helper_zone.get_zone_dependencies_of_entity_domain_name(web_site_dne)
                for ze in web_site_direct_zones:
                    zone_name_dependencies_of_wse.add(ze.name)
            except DoesNotExist:
                pass  # could be a TLD that are not considered
            for w_server_e in w_server_es:
                try:
                    web_server_direct_zones = helper_zone.get_zone_dependencies_of_entity_domain_name(w_server_e.name)
                    for ze in web_server_direct_zones:
                        zone_name_dependencies_of_wse.add(ze.name)
                except DoesNotExist:
                    pass  # could be a TLD that are not considered
            for zone_name in zone_name_dependencies_of_wse:
                rows.append([wse.url.string, zone_name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_5_query_zones_from_all_mail_domains(self):
        print(f"--- QUERY ZONES FROM MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        # PARAMETER
        mdes = helper_mail_domain.get_everyone()
        filename = 'mail_domains_zone_dependencies'
        # QUERY
        print(f"Parameters: {len(mdes)} mail domains retrieved from database.")
        rows = list()
        rows.append(["mail_domain", "zone_name"])
        for mde in mdes:
            try:
                ze_dependencies = helper_application_queries.get_all_zone_dependencies_from_mail_domain(mde)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            for ze in ze_dependencies:
                rows.append([mde.name.string, ze.name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_6_query_number_of_dependencies_of_all_mail_domains(self):
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF MAIL DOMAIN")
        # PARAMETER
        mdes = helper_mail_domain.get_everyone()
        filename = 'mail_domains_dependencies'
        # QUERY
        print(f"Parameters: {len(mdes)} mail domains retrieved from database.")
        rows = list()
        rows.append(['mail_domain', '#addresses', '#networks', '#as'])
        unresolved_mail_domain = 0
        unresolved_mail_server = 0
        no_as_for_ip_address = 0
        for mde in mdes:
            try:
                mses = helper_mail_server.get_every_of(mde)
            except DoesNotExist:
                print(f"NO MAIL SERVERS FOR {mde.name.string}")
                unresolved_mail_domain = unresolved_mail_domain + 1
                continue
            addresses = set()
            networks = set()
            autonomous_systems = set()
            for mse in mses:
                try:
                    iaes, dnes = helper_domain_name.resolve_access_path(mse.name, get_only_first_address=False)
                except (DoesNotExist, NoAvailablePathError):
                    print(f"{mse.name.string} IS NON-RESOLVABLE")
                    unresolved_mail_server = unresolved_mail_server + 1
                    continue
                for iae in iaes:
                    addresses.add(iae)
                    ine = helper_ip_network.get_of(iae)
                    networks.add(ine)
                    try:
                        ns_ase = helper_autonomous_system.get_of_entity_ip_address(iae)
                        autonomous_systems.add(ns_ase)
                    except DoesNotExist:
                        no_as_for_ip_address = no_as_for_ip_address + 1
            rows.append([mde.name.string, str(len(addresses)), str(len(networks)), str(len(autonomous_systems))])
        print(f"UNRESOLVED MAIL DOMAINS = {unresolved_mail_domain}")
        print(f"UNRESOLVED MAIL SERVERS = {unresolved_mail_server}")
        print(f"NO AS FOR IP ADDRESS = {no_as_for_ip_address}")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_7_query_number_of_dependencies_of_all_web_servers(self):
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF WEB SERVER")
        # PARAMETER
        wses = helper_web_server.get_everyone()
        filename = 'web_servers_dependencies'
        # QUERY
        print(f"Parameters: {len(wses)} web servers retrieved from database.")
        rows = list()
        rows.append(['web_server', '#addresses', '#networks', '#as'])
        unresolved_web_server = 0
        no_as_for_ip_address = 0
        for wse in wses:
            ip_networks = set()
            autonomous_systems = set()
            try:
                iaes, alias_dnes = helper_domain_name.resolve_access_path(wse.name, get_only_first_address=False)
            except DoesNotExist:
                print(f"{wse.name.string} IS NON-RESOLVABLE")
                unresolved_web_server = unresolved_web_server + 1
                continue
            for iae in iaes:
                ine = helper_ip_network.get_of(iae)
                ip_networks.add(ine)
                try:
                    ase = helper_autonomous_system.get_of_entity_ip_address(iae)
                except DoesNotExist:
                    print(f"NO AS FOR ADDRESS {iae.exploded}")
                    no_as_for_ip_address = no_as_for_ip_address + 1
                    continue
                autonomous_systems.add(ase)
            rows.append([wse.name.string, str(len(iaes)), str(len(ip_networks)), str(len(autonomous_systems))])
        print(f"UNRESOLVED WEB SERVER = {unresolved_web_server}")
        print(f"NO AS FOR IP ADDRESS = {no_as_for_ip_address}")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_8_query_networks_dependencies(self):
        print(f"--- QUERY NETWORKS DEPENDENCIES")
        # PARAMETER
        ines = helper_ip_network.get_everyone()
        filename = 'networks_dependencies'
        # QUERY
        print(f"Parameters: {len(ines)} IP networks retrieved from database.")
        rows = list()
        rows.append(['network', 'as_number', '#webservers', '#mailservers', '#nameservers', '#direct_zone_nameservers', '#zones_entire_contained', '#websites', '#maildomains'])
        for ine in ines:
            try:
                ase = helper_autonomous_system.get_of_entity_ip_network(ine)
            except DoesNotExist:
                continue
            try:
                network_iaes = helper_ip_address.get_all_of_entity_network(ine)
            except DoesNotExist:
                raise       # should never happen
            web_servers = set()
            mail_servers = set()
            name_servers = set()
            dz_name_servers = set()
            zones = set()
            web_sites = set()
            mail_domains = set()
            for iae in network_iaes:
                access_path_dnes = helper_ip_address.resolve_reversed_access_path(iae, add_dne_along_the_chain=True)
                # webservers
                for dne in access_path_dnes:
                    try:
                        wse, wse_dne = helper_web_server.get(dne.string)
                        web_servers.add(wse)
                    except DoesNotExist:
                        pass
                # mailservers
                for dne in access_path_dnes:
                    try:
                        mse = helper_mail_server.get(dne.string)
                        mail_servers.add(mse)
                    except DoesNotExist:
                        pass
                # nameservers
                for dne in access_path_dnes:
                    try:
                        nse, nse_dne = helper_name_server.get(dne.string)
                        name_servers.add(nse)
                    except DoesNotExist:
                        pass

            # dz_name_servers
            zes = helper_zone.get_everyone_that_is_direct_zone()
            for ze in zes:
                try:
                    nses = helper_name_server.get_all_from_zone_entity(ze)
                except DoesNotExist:
                    continue
                for nse in nses:
                    try:
                        nse_ines = helper_ip_network.get_of_entity_domain_name(nse.name)
                    except (DoesNotExist, NoAvailablePathError):
                        continue
                    if ine in nse_ines:
                        dz_name_servers.add(nse)

            # zones
            zo_dict = dict()        # to save up time from too much queries
            for nse in name_servers:
                zes = helper_zone.get_all_of_entity_name_server(nse)
                for ze in zes:
                    try:
                        zo = zo_dict[ze.name]
                    except KeyError:
                        zo = helper_zone.get_zone_object_from_zone_entity(ze)
                        zo_dict[ze.name] = zo
                    try:
                        all_nse_in_ine = ApplicationQueryExportingCSVTestCase.are_all_name_servers_of_zone_object_in_network(zo, ine)
                    except NoAvailablePathError:
                        all_nse_in_ine = False
                    if all_nse_in_ine:
                        zones.add(ze)
            # websites
            for ze in zones:
                dnes = helper_domain_name.get_from_direct_zone(ze)
                for dne in dnes:
                    try:
                        wsdnas = helper_web_site_domain_name.get_from_entity_domain_name(dne)
                        for wsdna in wsdnas:
                            web_sites.add(wsdna.web_site)
                    except DoesNotExist:
                        pass
            # mail_domains
            for ze in zones:
                dnes = helper_domain_name.get_from_direct_zone(ze)
                for dne in dnes:
                    try:
                        mde = helper_mail_domain.get(dne.string)
                        mail_domains.add(mde)
                    except DoesNotExist:
                        pass
            if len(dz_name_servers) > len(name_servers):
                print(f"!!! ERROR !!!")
            rows.append([ine.compressed_notation, ase.number, len(web_servers), len(mail_servers), len(name_servers), len(dz_name_servers), len(zones), len(web_sites), len(mail_domains)])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")


if __name__ == '__main__':
    unittest.main()
