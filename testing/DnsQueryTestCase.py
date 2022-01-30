import unittest
from datetime import datetime
from pathlib import Path
import dns
from dns.name import Name
from entities.resolvers.DnsResolver import DnsResolver
from entities.enums.TypesRR import TypesRR
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.UnknownReasonError import UnknownReasonError
from persistence.BaseModel import project_root_directory_name


class DnsQueryTestCase(unittest.TestCase):
    """
    Test class that doesn't assert any test, but simply prints all infos regarding a DNS query.
    Prints are executed through 2 tests:

    1- prints infos from the actual dnspython resolver object (RAW INFOS)

    2- prints infos from the DnsResolver object designed in this application

    They can be compared to see if the simplified DnsResolver object of this application is reliable.
    """
    import_cache_from_output_folder = None
    domain_name = None
    dns_resolver = None

    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == project_root_directory_name:
                return current
            else:
                current = current.parent

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_name = 'c.ns.c10r.facebook.com.'
        cls.domain_name = 'cdn-auth.digidentity.eu.'
        cls.domain_name = 'd1hljz92zxtrmu.cloudfront.net.'
        cls.type = TypesRR.CNAME
        cls.import_cache_from_output_folder = True
        # ELABORATION
        PRD = DnsQueryTestCase.get_project_root_folder()
        cls.dns_resolver = DnsResolver(None)
        if cls.import_cache_from_output_folder:
            try:
                cls.dns_resolver.cache.load_csv_from_output_folder(PRD)
            except FilenameNotFoundError:
                print(f"NO CACHE FILE FOUND")
        print(f"PARAMETER: {cls.domain_name}")

    def test_1_do_raw_query_and_prints_raw_infos(self):
        print(f"\n------- [1] START RAW QUERY TEST -------")
        try:
            answer = self.dns_resolver.resolver.resolve(self.domain_name, self.type.to_string())
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.YXDOMAIN, Exception) as e:  # name is a domain that does not exist
            print(f"!!! {str(e)} !!!")
            print(f"------- [1] END RAW QUERY TEST -------")
            return
        print(f"answer.canonical_name = {answer.canonical_name}")
        print(f"answer.qname = {answer.qname}")
        print(f"answer.nameserver = {answer.nameserver}")
        print(f"answer.type = {dns.rdatatype.to_text(answer.rdtype)}")
        print(f"answer.expiration = {answer.expiration} ==> [UTC]: {datetime.utcfromtimestamp(answer.expiration)}")
        if len(answer.chaining_result.cnames) != 0:
            print(f"answer.chaining_result.canonical_name = {answer.chaining_result.canonical_name}")
        for i, cname in enumerate(answer.chaining_result.cnames):
            print(f"\ncname[{i+1}/{len(answer.chaining_result.cnames)}]")
            print(f"--> cname.name = {cname.name}")
            print(f"--> cname.ttl = {cname.ttl}")
            for j, key in enumerate(cname.items.keys()):
                print(f"----> cname.item[{j+1}/{len(cname.items.keys())}] = {key}")
        print()
        for i, val in enumerate(answer):
            if isinstance(val, Name):
                print(f"value[{i+1}/{len(answer)}] = {str(val)}")
            else:
                print(f"value[{i+1}/{len(answer)}] = {val.to_text()}")
        print(f"------- [1] END RAW QUERY TEST -------")

    def test_2_do_query_and_debug_prints_from_application_resolver(self):
        print(f"\n------- [2] START QUERY TEST -------")
        try:
            rr_answer, rr_aliases = self.dns_resolver.do_query(self.domain_name, self.type)
        except (DomainNonExistentError, NoAnswerError, UnknownReasonError) as e:
            print(f"ERROR: {str(e)}")
            return
        print(f"Answer values:")
        print(f"rr = (name={rr_answer.name}, type={rr_answer.type}, values=[", end='')
        for i, value in enumerate(rr_answer.values):
            if i == len(rr_answer.values) - 1:
                print(f"{value}])")
            else:
                print(f"{value},", end='')
        print(f"\nAliases:")
        for i, rr_alias in enumerate(rr_aliases):
            print(f"rr[{i+1}]: (name={rr_alias.name}, type={rr_alias.type}, values=[", end='')
            for j, value in enumerate(rr_alias.values):
                if j == len(rr_alias.values) - 1:
                    print(f"{value}])")
                else:
                    print(f"{value},", end='')
        print(f"------- [2] END QUERY TEST -------")


if __name__ == '__main__':
    unittest.main()
