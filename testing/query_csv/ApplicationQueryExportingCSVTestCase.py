import csv
import unittest
from datetime import datetime
from pathlib import Path
from typing import List
from peewee import DoesNotExist
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_web_server, helper_zone, helper_web_site, helper_domain_name, helper_mail_domain, \
    helper_mail_server, helper_name_server, helper_autonomous_system, helper_ip_network, helper_direct_zone, \
    helper_application_queries
from persistence.BaseModel import db
from utils import file_utils, csv_utils, datetime_utils


# TODO: eccezioni nelle query...
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

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.sub_folder = 'output'
        cls.separator = ','
        cls.unresolved_value = 'ND'
        #
        cls.PRD = file_utils.get_project_root_directory()

    def execute_query_1(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'zone_infos'
        # QUERY
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF ZONE NAME")
        result = helper_application_queries.do_query_1()
        rows = ["zone_name", "#nameservers", "#networks", "#as"]
        for tupl in result:
            rows.append([tupl[0].name, str(len(tupl[1])), str(len(tupl[2])), str(len(tupl[3]))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_1_query_number_of_dependencies_of_all_zones(self):
        start_time = datetime.now()
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF ZONE NAME")
        # PARAMETER
        zes = helper_zone.get_everyone()
        # this flag tells if we have to export a zone name that we know it is a zone (NS RR was resolved) but each
        # nameserver's A RR was not resolved. In that case the zone row will be added and for each field regarding the
        # relative infos will present the string value: ND
        only_complete_zones = False
        filename = 'zone_infos'
        # QUERY
        print(f"Parameters: {len(zes)} zones retrieved from database.")
        rows = list()
        rows.append(["zone_name", "#nameservers", "#networks", "#as"])
        count_complete_zones = 0
        count_incomplete_zones = 0
        with db.atomic():
            for ze in zes:
                try:
                    nses = helper_name_server.get_zone_nameservers(ze)
                except NoDisposableRowsError as e:
                    self.fail(f"!!! {str(e)} !!!")
                ases = set()
                iaes = set()
                ines = set()
                is_unresolved = False
                for nse in nses:
                    try:
                        cname_dnes, dne_iaes = helper_domain_name.resolve_a_path(nse.name, as_persistence_entities=True)
                        # a_path = helper_domain_name.resolve_a_path(nse.name, as_persistence_entities=False)
                    except (DoesNotExist, NoAvailablePathError):
                        is_unresolved = True
                        break
                    for iae in dne_iaes:
                        iaes.add(iae)
                        try:
                            ine = helper_ip_network.get_of(iae)
                        except (DoesNotExist, NoAvailablePathError):
                            raise
                        ines.add(ine)
                        try:
                            ase = helper_autonomous_system.get_of_ip_address(iae)
                        except DoesNotExist:
                            print('')
                            continue        # TODO
                        ases.add(ase)
                if not only_complete_zones and is_unresolved:
                    rows.append([ze.name, self.unresolved_value, self.unresolved_value, self.unresolved_value])
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
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def execute_query_2(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'web_sites_direct_zone_dependencies'
        # QUERY
        print(f"--- QUERY DIRECT ZONES OF ALL WEB SITES AND ASSOCIATED WEB SERVERS")
        result = helper_application_queries.do_query_2()
        rows = ['web_site', 'zone_name']
        for tupl in result:
            rows.append([tupl[0].url.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_2_query_direct_zones_of_all_web_sites(self):
        start_time = datetime.now()
        print(f"--- QUERY DIRECT ZONES OF ALL WEB SITES AND ASSOCIATED WEB SERVERS")
        # PARAMETER
        web_site_entities = helper_web_site.get_everyone()
        filename = 'web_sites_direct_zone_dependencies'
        # QUERY
        print(f"Parameters: {len(web_site_entities)} web sites retrieved from database.")
        rows = list()
        rows.append(['web_site', 'zone_name'])
        with db.atomic():
            for web_site_entity in web_site_entities:
                #
                https_web_server_entity, http_web_server_entity = helper_web_server.get_from(web_site_entity)
                try:
                    web_site_domain_name_entity = helper_domain_name.get_of(web_site_entity)
                except DoesNotExist:
                    raise
                #
                direct_zones_of_web_site = set()
                try:
                    ze = helper_zone.get_direct_zone_of(https_web_server_entity.name)
                    direct_zones_of_web_site.add(ze)
                except DoesNotExist:
                    pass          # could be a TLD that are not considered
                if http_web_server_entity != https_web_server_entity:
                    try:
                        ze = helper_zone.get_direct_zone_of(http_web_server_entity.name)
                        direct_zones_of_web_site.add(ze)
                    except DoesNotExist:
                        pass      # could be a TLD that are not considered
                try:
                    ze = helper_zone.get_direct_zone_of(web_site_domain_name_entity)
                    direct_zones_of_web_site.add(ze)
                except DoesNotExist:
                    pass          # could be a TLD that are not considered
                for ze in direct_zones_of_web_site:
                    rows.append([web_site_entity.url.string, ze.name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def execute_query_3(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'mail_domains_direct_zone_dependencies'
        # QUERY
        print(f"--- QUERY DIRECT ZONES OF ALL MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        result = helper_application_queries.do_query_3()
        rows = ['mail_domain', 'zone_name']
        for tupl in result:
            rows.append([tupl[0].name.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_3_query_direct_zones_of_all_mail_domains(self):
        start_time = datetime.now()
        print(f"--- QUERY DIRECT ZONES OF ALL MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        # PARAMETER
        mail_domain_entities = helper_mail_domain.get_everyone()
        filename = 'mail_domains_direct_zone_dependencies'
        # QUERY
        print(f"Parameters: {len(mail_domain_entities)} mail domains retrieved from database.")
        rows = list()
        rows.append(['mail_domain', 'zone_name'])
        with db.atomic():
            for mail_domain_entity in mail_domain_entities:
                #
                try:
                    mail_server_entities_of_mail_domain = helper_mail_server.get_every_of(mail_domain_entity)
                except DoesNotExist as e:
                    self.fail(f"!!! {str(e)} !!!")
                #
                direct_zones_of_mail_domain = set()
                try:
                    ze = helper_zone.get_direct_zone_of(mail_domain_entity.name)
                    direct_zones_of_mail_domain.add(ze)
                except DoesNotExist:
                    pass
                for mail_server_entity in mail_server_entities_of_mail_domain:
                    try:
                        ze = helper_zone.get_direct_zone_of(mail_server_entity.name)
                        direct_zones_of_mail_domain.add(ze)
                    except DoesNotExist:
                        pass
                for ze in direct_zones_of_mail_domain:
                    rows.append([mail_domain_entity.name.string, ze.name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def execute_query_4(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'web_sites_zone_dependencies'
        # QUERY
        print(f"--- QUERY ZONE DEPENDENCIES OF WEB SITES AND ASSOCIATED WEB SERVERS")
        result = helper_application_queries.do_query_4()
        rows = ['web_site', 'zone_name']
        for tupl in result:
            rows.append([tupl[0].url.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_4_query_zone_dependencies_of_all_web_sites(self):
        start_time = datetime.now()
        print(f"--- QUERY ZONE DEPENDENCIES OF WEB SITES AND ASSOCIATED WEB SERVERS")
        # PARAMETER
        web_site_entities = helper_web_site.get_everyone()
        filename = 'web_sites_zone_dependencies'
        # QUERY
        print(f"Parameters: {len(web_site_entities)} web sites retrieved from database.")
        rows = list()
        rows.append(['web_site', 'zone_name'])
        with db.atomic():
            for web_site_entity in web_site_entities:
                #
                https_web_server_entity, http_web_server_entity = helper_web_server.get_from(web_site_entity)
                try:
                    web_site_domain_name_entity = helper_domain_name.get_of(web_site_entity)
                except DoesNotExist:
                    raise
                #
                zone_dependencies_of_web_site = set()
                try:
                    zes = helper_zone.get_zone_dependencies_of_entity_domain_name(https_web_server_entity.name)
                    for ze in zes:
                        zone_dependencies_of_web_site.add(ze)
                except DoesNotExist:
                    pass
                if http_web_server_entity != https_web_server_entity:
                    try:
                        zes = helper_zone.get_zone_dependencies_of_entity_domain_name(http_web_server_entity.name)
                        for ze in zes:
                            zone_dependencies_of_web_site.add(ze)
                    except DoesNotExist:
                        pass
                try:
                    zes = helper_zone.get_zone_dependencies_of_entity_domain_name(web_site_domain_name_entity)
                    for ze in zes:
                        zone_dependencies_of_web_site.add(ze)
                except DoesNotExist:
                    pass
                for ze in zone_dependencies_of_web_site:
                    rows.append([web_site_entity.url.string, ze.name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def execute_query_5(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'mail_domains_zone_dependencies'
        # QUERY
        print(f"--- QUERY ZONE DEPENDENCIES OF MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        result = helper_application_queries.do_query_5()
        rows = ['web_site', 'zone_name']
        for tupl in result:
            rows.append([tupl[0].name.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_5_query_zones_dependencies_of_all_mail_domains(self):
        start_time = datetime.now()
        print(f"--- QUERY ZONE DEPENDENCIES OF MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        # PARAMETER
        mail_domain_entities = helper_mail_domain.get_everyone()
        filename = 'mail_domains_zone_dependencies'
        # QUERY
        print(f"Parameters: {len(mail_domain_entities)} mail domains retrieved from database.")
        rows = list()
        rows.append(["mail_domain", "zone_name"])
        with db.atomic():
            for mail_domain_entity in mail_domain_entities:
                #
                try:
                    mail_server_entities_of_mail_domain = helper_mail_server.get_every_of(mail_domain_entity)
                except DoesNotExist as e:
                    self.fail(f"!!! {str(e)} !!!")
                #
                zone_dependencies_of_web_site = set()
                try:
                    zes = helper_zone.get_zone_dependencies_of_entity_domain_name(mail_domain_entity.name)
                    for ze in zes:
                        zone_dependencies_of_web_site.add(ze)
                except DoesNotExist:
                    pass
                for mail_server_entity in mail_server_entities_of_mail_domain:
                    try:
                        zes = helper_zone.get_zone_dependencies_of_entity_domain_name(mail_server_entity.name)
                        for ze in zes:
                            zone_dependencies_of_web_site.add(ze)
                    except DoesNotExist:
                        pass
                for ze in zone_dependencies_of_web_site:
                    rows.append([mail_domain_entity.name.string, ze.name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def execute_query_6(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'mail_domains_dependencies'
        # QUERY
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF MAIL DOMAIN")
        result = helper_application_queries.do_query_6()
        rows = ['mail_domain', '#mailservers', '#networks', '#as']
        for tupl in result:
            rows.append([tupl[0].name.string, str(len(tupl[1])), str(len(tupl[2])), str(len(tupl[3]))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_6_query_number_of_dependencies_of_all_mail_domains(self):
        start_time = datetime.now()
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF MAIL DOMAIN")
        # PARAMETER
        mail_domain_entities = helper_mail_domain.get_everyone()
        filename = 'mail_domains_dependencies'
        only_complete_mail_domain = False
        # QUERY
        print(f"Parameters: {len(mail_domain_entities)} mail domains retrieved from database.")
        rows = list()
        rows.append(['mail_domain', '#mailservers', '#networks', '#as'])
        count_unresolved_mail_domain = 0
        count_resolved_mail_domain = 0
        with db.atomic():
            for mail_domain_entity in mail_domain_entities:
                #
                try:
                    mail_server_entities_of_mail_domain = helper_mail_server.get_every_of(mail_domain_entity)
                except DoesNotExist as e:
                    self.fail(f"!!! {str(e)} !!!")
                #
                ip_addresses_of_mail_domain = set()
                ip_networks_of_mail_domain = set()
                autonomous_systems_of_mail_domain = set()
                for mail_server_entity in mail_server_entities_of_mail_domain:
                    try:
                        cname_chain, iaes = helper_domain_name.resolve_a_path(mail_server_entity.name, as_persistence_entities=True)
                    except NoAvailablePathError:
                        continue
                    for iae in iaes:
                        ip_addresses_of_mail_domain.add(iae)
                        try:
                            ine = helper_ip_network.get_of(iae)
                        except DoesNotExist:
                            raise
                        ip_networks_of_mail_domain.add(ine)
                        try:
                            ase = helper_autonomous_system.get_of_ip_address(iae)
                        except DoesNotExist:
                            continue
                        autonomous_systems_of_mail_domain.add(ase)
                rows.append([mail_domain_entity.name.string, str(len(ip_addresses_of_mail_domain)), str(len(ip_networks_of_mail_domain)), str(len(autonomous_systems_of_mail_domain))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def execute_query_7(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'web_servers_dependencies'
        # QUERY
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF WEB SERVER")
        result = helper_application_queries.do_query_7()
        rows = ['web_server', '#addresses', '#networks', '#as']
        for tupl in result:
            rows.append([tupl[0].name.string, str(len(tupl[1])), str(len(tupl[2])), str(len(tupl[3]))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_7_query_number_of_dependencies_of_all_web_servers(self):
        start_time = datetime.now()
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF WEB SERVER")
        # PARAMETER
        web_server_entities = helper_web_server.get_everyone()
        filename = 'web_servers_dependencies'
        # QUERY
        print(f"Parameters: {len(web_server_entities)} web servers retrieved from database.")
        rows = list()
        rows.append(['web_server', '#addresses', '#networks', '#as'])
        with db.atomic():
            for web_server_entity in web_server_entities:
                ip_addresses_of_web_server = set()
                ip_networks_of_web_server = set()
                autonomous_systems_of_web_server = set()
                try:
                    cname_chain, iaes = helper_domain_name.resolve_a_path(web_server_entity.name, as_persistence_entities=True)
                except NoAvailablePathError:
                    continue
                for iae in iaes:
                    ip_addresses_of_web_server.add(iae)
                    try:
                        ine = helper_ip_network.get_of(iae)
                    except DoesNotExist:
                        raise
                    ip_networks_of_web_server.add(ine)
                    try:
                        ase = helper_autonomous_system.get_of_ip_address(iae)
                    except DoesNotExist:
                        continue
                    autonomous_systems_of_web_server.add(ase)
                rows.append([web_server_entity.name.string, str(len(ip_addresses_of_web_server)), str(len(ip_networks_of_web_server)), str(len(autonomous_systems_of_web_server))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def execute_query_8(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'networks_dependencies'
        # QUERY
        print(f"--- QUERY NETWORKS DEPENDENCIES")
        result = helper_application_queries.do_query_8()
        rows = ['network', 'as_number', 'as_description', '#belonging_webservers', '#belonging_mailservers', '#belonging_mailservers', '#zones_entirely_contained', '#website_directzones_entirely_contained', '#maildomain_directzones_entirely_contained', '#maildomain_directzone_entirely_contained']
        for tupl in result:
            rows.append([
                tupl[0].compressed_notation,
                str(tupl[1].number),
                tupl[1].description,
                str(len(tupl[2])),
                str(len(tupl[3])),
                str(len(tupl[4])),
                str(len(tupl[5])),
                str(len(tupl[6])),
                str(len(tupl[7]))
            ])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    #TODO
    def test_8_query_networks_dependencies(self):
        start_time = datetime.now()
        print(f"--- QUERY NETWORKS DEPENDENCIES")
        # PARAMETER
        network_entities = helper_ip_network.get_everyone()
        filename = 'networks_dependencies'
        # QUERY
        print(f"Parameters: {len(network_entities)} IP networks retrieved from database.")
        rows = list()
        rows.append(['network', 'as_number', 'as_description', '#belonging_webservers', '#belonging_mailservers', '#belonging_mailservers', '#zones_entirely_contained', '#website_directzones_entirely_contained', '#maildomain_directzones_entirely_contained', '#maildomain_directzone_entirely_contained'])
        with db.atomic():
            for network_entity in network_entities:
                try:
                    autonomous_system = helper_autonomous_system.get_of_entity_ip_network(network_entity)
                except DoesNotExist:
                    print(f"{network_entity.compressed_notation} does not exist..")
                    continue
                try:
                    dnes = helper_domain_name.get_everyone_from_ip_network(network_entity)
                except NoDisposableRowsError:
                    raise
                try:
                    belonging_webservers = helper_web_server.filter_domain_names(dnes)
                except NoDisposableRowsError:
                    belonging_webservers = set()
                try:
                    belonging_mailservers = helper_mail_server.filter_domain_names(dnes)
                except NoDisposableRowsError:
                    belonging_mailservers = set()
                try:
                    belonging_nameservers = helper_mail_server.filter_domain_names(dnes)
                except NoDisposableRowsError:
                    belonging_nameservers = set()
                try:
                    zones_entirely_contained = helper_zone.get_entire_zones_from_nameservers_pool(belonging_nameservers)
                except NoDisposableRowsError:
                    zones_entirely_contained = set()
                try:
                    direct_zones = helper_direct_zone.get_from_zone_dataset(zones_entirely_contained)
                except NoDisposableRowsError:
                    direct_zones = set()
                website_directzones_entirely_contained = set()
                maildomain_directzones_entirely_contained = set()
                # TODO



                rows.append([
                    network_entity.compressed_notation,
                    str(autonomous_system.number),
                    autonomous_system.description,
                    str(len(belonging_webservers)),
                    str(len(belonging_mailservers)),
                    str(len(belonging_nameservers)),
                    str(len(zones_entirely_contained)),
                    str(len(website_directzones_entirely_contained)),
                    str(len(maildomain_directzones_entirely_contained))
                ])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        PRD = file_utils.get_project_root_directory()
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", PRD)
        ApplicationQueryExportingCSVTestCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")


if __name__ == '__main__':
    unittest.main()
