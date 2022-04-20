import csv
import unittest
from datetime import datetime
from pathlib import Path
from typing import List
from persistence import helper_application_queries
from utils import file_utils, csv_utils, datetime_utils


class ApplicationQueryCSVExportCase(unittest.TestCase):
    @staticmethod
    def write_csv_file(file: Path, separator: str, rows: List[List[str]]) -> None:
        try:
            with file.open('w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, dialect=f'{csv_utils.return_personalized_dialect_name(separator)}')
                for row in rows:
                    writer.writerow(row)
                f.close()
        except (PermissionError, FileNotFoundError, OSError):
            raise

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.sub_folder = 'output'
        cls.separator = ','
        cls.unresolved_value = 'ND'
        #
        cls.PRD = file_utils.get_project_root_directory()

    def test_execute_query_1(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'zone_infos'
        # QUERY
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF ZONE NAME")
        result = helper_application_queries.do_query_1()
        rows = [["zone_name", "#nameservers", "#networks", "#as"]]
        for tupl in result:
            rows.append([tupl[0].name, str(len(tupl[1])), str(len(tupl[2])), str(len(tupl[3]))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_execute_query_2(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'web_sites_direct_zone_dependencies'
        # QUERY
        print(f"--- QUERY DIRECT ZONES OF ALL WEB SITES AND ASSOCIATED WEB SERVERS")
        result = helper_application_queries.do_query_2()
        rows = [['web_site', 'zone_name']]
        for tupl in result:
            rows.append([tupl[0].url.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_execute_query_3(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'mail_domains_direct_zone_dependencies'
        # QUERY
        print(f"--- QUERY DIRECT ZONES OF ALL MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        result = helper_application_queries.do_query_3()
        rows = [['mail_domain', 'zone_name']]
        for tupl in result:
            rows.append([tupl[0].name.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_execute_query_4(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'web_sites_zone_dependencies'
        # QUERY
        print(f"--- QUERY ZONE DEPENDENCIES OF WEB SITES AND ASSOCIATED WEB SERVERS")
        result = helper_application_queries.do_query_4()
        rows = [['web_site', 'zone_name']]
        for tupl in result:
            rows.append([tupl[0].url.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_execute_query_5(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'mail_domains_zone_dependencies'
        # QUERY
        print(f"--- QUERY ZONE DEPENDENCIES OF MAIL DOMAIN AND ASSOCIATED MAIL SERVERS")
        result = helper_application_queries.do_query_5()
        rows = [['mail_domain', 'zone_name']]
        for tupl in result:
            rows.append([tupl[0].name.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_execute_query_6(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'mail_domains_dependencies'
        # QUERY
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF MAIL DOMAIN")
        result = helper_application_queries.do_query_6()
        rows = [['mail_domain', '#mailservers', '#networks', '#as']]
        for tupl in result:
            rows.append([tupl[0].name.string, str(len(tupl[1])), str(len(tupl[2])), str(len(tupl[3]))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_execute_query_7(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'web_servers_dependencies'
        # QUERY
        print(f"--- QUERY NUMBER OF DEPENDENCIES OF WEB SERVER")
        result = helper_application_queries.do_query_7()
        rows = [['web_server', '#addresses', '#networks', '#as']]
        for tupl in result:
            rows.append([tupl[0].name.string, str(len(tupl[1])), str(len(tupl[2])), str(len(tupl[3]))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")

    def test_execute_query_8(self):
        start_time = datetime.now()
        # PARAMETER
        filename = 'networks_dependencies'
        # QUERY
        print(f"--- QUERY NETWORKS DEPENDENCIES")
        result = helper_application_queries.do_query_8()
        rows = [['network', 'as_number', 'as_description', '#belonging_webservers', '#belonging_mailservers', '#belonging_mailservers', '#zones_entirely_contained', '#website_directzones_entirely_contained', '#maildomain_directzones_entirely_contained', '#maildomain_directzone_entirely_contained']]
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
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END ---\n")


if __name__ == '__main__':
    unittest.main()
