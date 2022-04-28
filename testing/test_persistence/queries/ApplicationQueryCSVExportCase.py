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
        """
        This query computes data regarding the architecture of every single zone in the database.

        Example:
        zone_name1, number of nameservers (addresses), number of networks, number of as
        zone_name2, number of nameservers (addresses), number of networks, number of as
        zone_name3, number of nameservers (addresses), number of networks, number of as
        """
        start_time = datetime.now()
        # PARAMETER
        filename = 'zone_infos'
        # QUERY
        print(f"--- START QUERY 1 ---")
        result = helper_application_queries.do_query_1()
        rows = [["zone_name", "#nameservers", "#networks", "#as"]]
        for tupl in result:
            rows.append([tupl[0].name, str(len(tupl[1])), str(len(tupl[2])), str(len(tupl[3]))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END QUERY 1 ---\n")

    def test_execute_query_2(self):
        """
        This query computes direct zones of every website in the database.

        Example:
        web_site1, zone1
        web_site1, zone2
        web_site2, zone3
        """
        start_time = datetime.now()
        # PARAMETER
        filename = 'web_sites_direct_zone_dependencies'
        # QUERY
        print(f"--- START QUERY 2 ---")
        result = helper_application_queries.do_query_2()
        rows = [['web_site', 'zone_name']]
        for tupl in result:
            rows.append([tupl[0].url.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END QUERY 2 ---\n")

    def test_execute_query_3(self):
        """
        This query computes direct zones of every mail domain in the database.

        Example:
        mail_domain1, zone1
        mail_domain2, zone2
        mail_domain2, zone3
        """
        start_time = datetime.now()
        # PARAMETER
        filename = 'mail_domains_direct_zone_dependencies'
        # QUERY
        print(f"--- START QUERY 3 ---")
        result = helper_application_queries.do_query_3()
        rows = [['mail_domain', 'zone_name']]
        for tupl in result:
            rows.append([tupl[0].name.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END QUERY 3 ---\n")

    def test_execute_query_4(self):
        """
        This query computes zone dependencies of every website in the database.

        Example:
        web_site1, zone1
        web_site1, zone2
        web_site1, zone3
        web_site2, zone3
        web_site2, zone4
        """
        start_time = datetime.now()
        # PARAMETER
        filename = 'web_sites_zone_dependencies'
        # QUERY
        print(f"--- START QUERY 4 ---")
        result = helper_application_queries.do_query_4()
        rows = [['web_site', 'zone_name']]
        for tupl in result:
            rows.append([tupl[0].url.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END QUERY 4 ---\n")

    def test_execute_query_5(self):
        """
        This query computes zone dependencies of every mail domain in the database.

        Example:
        mail_domain1, zone1
        mail_domain1, zone2
        mail_domain1, zone3
        mail_domain2, zone3
        mail_domain2, zone4
        """
        start_time = datetime.now()
        # PARAMETER
        filename = 'mail_domains_zone_dependencies'
        # QUERY
        print(f"--- START QUERY 5 ---")
        result = helper_application_queries.do_query_5()
        rows = [['mail_domain', 'zone_name']]
        for tupl in result:
            rows.append([tupl[0].name.string, tupl[1].name])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END QUERY 5 ---\n")

    def test_execute_query_6(self):
        """
        This query computes data regarding the architecture of every mail domain in the database.

        Example:
        mail_domain1, number of mail servers (addresses), number of networks, number of as
        mail_domain2, number of mail servers (addresses), number of networks, number of as
        """
        start_time = datetime.now()
        # PARAMETER
        filename = 'mail_domains_dependencies'
        # QUERY
        print(f"--- START QUERY 6 ---")
        result = helper_application_queries.do_query_6()
        rows = [['mail_domain', '#mailservers', '#networks', '#as']]
        for tupl in result:
            rows.append([tupl[0].name.string, str(len(tupl[1])), str(len(tupl[2])), str(len(tupl[3]))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END QUERY 6 ---\n")

    def test_execute_query_7(self):
        """
        This query computes data regarding the architecture of every webserver in the database.

        Example:
        web_server1, number of addresses, number of networks, number of as
        web_server2, number of addresses, number of networks, number of as
        web_server3, number of addresses, number of networks, number of as
        """
        start_time = datetime.now()
        # PARAMETER
        filename = 'web_servers_dependencies'
        # QUERY
        print(f"--- START QUERY 7 ---")
        result = helper_application_queries.do_query_7()
        rows = [['web_server', '#addresses', '#networks', '#as']]
        for tupl in result:
            rows.append([tupl[0].name.string, str(len(tupl[1])), str(len(tupl[2])), str(len(tupl[3]))])
        print(f"Written {len(rows)} rows.")
        # EXPORTING
        file = file_utils.set_file_in_folder(self.sub_folder, filename + ".csv", self.PRD)
        ApplicationQueryCSVExportCase.write_csv_file(file, self.separator, rows)
        print(f"Execution time: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"--- END QUERY 7 ---\n")

    def test_execute_query_8(self):
        """
        Network query...

        Example:
        network, as, number of ..., number of ..
        """
        start_time = datetime.now()
        # PARAMETER
        filename = 'networks_dependencies'
        # QUERY
        print(f"--- START QUERY 8 ---")
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
        print(f"--- END QUERY 8 ---\n")


if __name__ == '__main__':
    unittest.main()
