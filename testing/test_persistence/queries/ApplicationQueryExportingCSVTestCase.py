import csv
import unittest
from pathlib import Path
from typing import List
from peewee import DoesNotExist
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_web_server, helper_zone, helper_web_site, helper_domain_name, helper_mail_domain, \
    helper_mail_server, helper_name_server, helper_autonomous_system, helper_ip_network, helper_application_queries
from persistence.BaseModel import project_root_directory_name
from utils import file_utils, csv_utils


class ApplicationQueryExportingCSVTestCase(unittest.TestCase):
    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == project_root_directory_name:
                return current
            else:
                current = current.parent

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

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.sub_folder = 'output'
        cls.separator = ','

    def test_1_query_number_of_dependencies_of_all_zones(self):
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF ZONE NAME")
        # PARAMETER
        zes = helper_zone.get_everyone()
        filename = 'query_number_of_dependencies_of_all_zones'
        # QUERY
        print(f"Parameters: {len(zes)} zones retrieved from database.")
        rows = list()
        for ze in zes:
            try:
                nses = helper_name_server.get_all_from_zone_entity(ze)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            ases = set()
            ines = set()
            for nse in nses:
                try:
                    ns_ines = helper_ip_network.get_of_entity_domain_name(nse.name)
                except (DoesNotExist, NoAvailablePathError) as e:
                    continue
                for ns_ine in ns_ines:
                    ines.add(ns_ine)
                ns_ases = helper_autonomous_system.get_of_entity_domain_name(nse.name)
                for ns_ase in ns_ases:
                    ases.add(ns_ase)
            row = [ze.name, str(len(nses)), str(len(ines)), str(len(ases))]
            rows.append(row)
        # EXPORTING
        PRD = ApplicationQueryExportingCSVTestCase.get_project_root_folder()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_2_query_direct_zones_from_all_web_sites(self):
        print(f"--- QUERY DIRECT ZONES FROM WEB SITES AND ASSOCIATED WEB SERVERS")
        # PARAMETER
        wses = helper_web_site.get_everyone()
        filename = 'query_direct_zones_from_all_web_sites'
        # QUERY
        print(f"Parameters: {len(wses)} web sites retrieved from database.")
        rows = list()
        for wse in wses:
            w_server_es = helper_web_server.get_from_entity_web_site(wse)
            try:
                web_site_dne = helper_domain_name.get_from_entity_web_site(wse)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
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
        # EXPORTING
        PRD = ApplicationQueryExportingCSVTestCase.get_project_root_folder()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_3_query_direct_zones_from_all_mail_domains(self):
        print(f"--- QUERY DIRECT ZONES FROM MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        # PARAMETER
        mdes = helper_mail_domain.get_everyone()
        filename = 'query_direct_zones_from_all_mail_domains'
        # QUERY
        print(f"Parameters: {len(mdes)} mail domains retrieved from database.")
        rows = list()
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
        # EXPORTING
        PRD = ApplicationQueryExportingCSVTestCase.get_project_root_folder()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_4_query_zones_from_all_web_sites(self):
        print(f"--- QUERY ZONES FROM WEB SITES AND ASSOCIATED WEB SERVERS")
        # PARAMETER
        wses = helper_web_site.get_everyone()
        filename = 'query_zones_from_all_web_sites'
        # QUERY
        print(f"Parameters: {len(wses)} web sites retrieved from database.")
        rows = list()
        for wse in wses:
            try:
                ze_dependencies = helper_application_queries.get_all_zone_dependencies_from_web_site(wse, from_script_sites=False)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            for ze in ze_dependencies:
                rows.append([wse.url.string, ze.name])
        # EXPORTING
        PRD = ApplicationQueryExportingCSVTestCase.get_project_root_folder()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_5_query_zones_from_all_mail_domains(self):
        print(f"--- QUERY ZONES FROM MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        # PARAMETER
        mdes = helper_mail_domain.get_everyone()
        filename = 'query_zones_from_all_mail_domains'
        # QUERY
        print(f"Parameters: {len(mdes)} mail domains retrieved from database.")
        rows = list()
        for mde in mdes:
            try:
                ze_dependencies = helper_application_queries.get_all_zone_dependencies_from_mail_domain(mde)
            except DoesNotExist as e:
                self.fail(f"!!! {str(e)} !!!")
            for ze in ze_dependencies:
                rows.append([mde.name.string, ze.name])
        # EXPORTING
        PRD = ApplicationQueryExportingCSVTestCase.get_project_root_folder()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_6_query_number_of_dependencies_of_all_mail_domains(self):
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF MAIL DOMAIN")
        # PARAMETER
        mdes = helper_mail_domain.get_everyone()
        filename = 'query_number_of_dependencies_of_all_mail_domains'
        # QUERY
        print(f"Parameters: {len(mdes)} mail domains retrieved from database.")
        rows = list()
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
        PRD = ApplicationQueryExportingCSVTestCase.get_project_root_folder()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")

    def test_7_query_number_of_dependencies_of_all_web_servers(self):
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF WEB SERVER")
        # PARAMETER
        wses = helper_web_server.get_everyone()
        filename = 'query_number_of_dependencies_of_all_web_servers'
        # QUERY
        print(f"Parameters: {len(wses)} web servers retrieved from database.")
        rows = list()
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
        PRD = ApplicationQueryExportingCSVTestCase.get_project_root_folder()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"--- END ---\n")


if __name__ == '__main__':
    unittest.main()
