import unittest
from pathlib import Path
from entities.DnsResolver import DnsResolver
from entities.TypesRR import TypesRR
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.UnknownReasonError import UnknownReasonError


class DnsQueryTestCase(unittest.TestCase):
    domain_name = None
    dns_resolver = None

    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == 'LavoroTesi':
                return current
            else:
                current = current.parent

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_name = 'units09.cineca.it.'
        cls.type = TypesRR.A
        # ELABORATION
        PRD = DnsQueryTestCase.get_project_root_folder()
        cls.dns_resolver = DnsResolver([])
        try:
            cls.dns_resolver.cache.load_csv_from_output_folder(PRD)
        except FilenameNotFoundError:
            print(f"NO CACHE FILE FOUND")
        print(f"PARAMETER: {cls.domain_name}")

    def test_1_do_query_and_debug_prints(self):
        print(f"\nSTART QUERY TEST")
        try:
            rr_answer, rr_aliases = self.dns_resolver.do_query(self.domain_name, self.type)
        except (DomainNonExistentError, NoAnswerError, UnknownReasonError) as e:
            print(f"ERROR: {str(e)}")
            exit(1)
        print(f"Answer values:")
        print(f"(name={rr_answer.name}, values=[", end='')
        for i, value in enumerate(rr_answer.values):
            if i == len(rr_answer.values) - 1:
                print(f"{value}])")
            else:
                print(f"{value},", end='')
        print(f"\nAliases:")
        for i, rr_alias in enumerate(rr_aliases):
            print(f"[{i+1}]: (name={rr_alias.name}, values=[", end='')
            for j, value in enumerate(rr_alias.values):
                if j == len(rr_alias.values) - 1:
                    print(f"{value}])")
                else:
                    print(f"{value},", end='')
        print(f"END QUERY TEST")


if __name__ == '__main__':
    unittest.main()
