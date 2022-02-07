import csv
import unittest
from pathlib import Path
from typing import List
import dns.resolver
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from persistence import helper_mail_domain
from persistence.BaseModel import project_root_directory_name
from utils import file_utils, csv_utils


class QueryTXTRRecordsTestCase(unittest.TestCase):
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

    @staticmethod
    def dns_read_TXT(my_resolver, name):
        retval = []
        try:
            answers = my_resolver.resolve(name, 'TXT')
            for rdata in answers:
                for txt_string in rdata.strings:
                    retval.append(txt_string)
        except BaseException as err:
            pass
        return retval

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.mtasts_query = False
        # ELABORATION
        cls.my_resolver = dns.resolver.Resolver()
        PRD = QueryTXTRRecordsTestCase.get_project_root_folder()
        try:
            file = file_utils.search_for_filename_in_subdirectory('output', 'every_mail_domain.csv', project_root_directory=PRD)
        except FilenameNotFoundError:
            mdes = helper_mail_domain.get_everyone()
            rows = list()
            for mde in mdes:
                rows.append([mde.name.string])
            file = file_utils.set_file_in_folder('output', "every_mail_domain.csv", PRD)
            QueryTXTRRecordsTestCase.write_csv_file(file, ',', rows)
        finally:
            with open(str(file), newline='') as f:
                reader = csv.reader(f)
                cls.data = list(reader)

    def test_do_queries(self):
        txt_records = []
        for d in self.data:
            if self.mtasts_query:
                records = QueryTXTRRecordsTestCase.dns_read_TXT(self.my_resolver, '_mta-sts.' + d[0])
            else:
                records = QueryTXTRRecordsTestCase.dns_read_TXT(self.my_resolver, d[0])

            values = ' '.join([str(elem) for elem in records])
            txt_records.append((d[0], len(records), values))

        if self.mtasts_query:
            new_file = file_utils.set_file_in_folder('output', 'TXT_mta-sts_mail_domains.csv')
        else:
            new_file = file_utils.set_file_in_folder('output', 'TXT_mail_domains.csv')
        with open(str(new_file), 'w', newline='') as f:
            writer = csv.writer(f)
            if self.mtasts_query:
                writer.writerow(['mail_domain', '_mta-sts TXT RR'])
            else:
                writer.writerow(['mail_domain', 'TXT RR'])

            writer.writerows(txt_records)


if __name__ == '__main__':
    unittest.main()
