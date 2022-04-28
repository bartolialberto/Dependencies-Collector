import unittest
from datetime import datetime
import dns
from dns.name import Name
from entities.resolvers.DnsResolver import DnsResolver
from entities.enums.TypesRR import TypesRR
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.UnknownReasonError import UnknownReasonError


class DnsQueryTestCase(unittest.TestCase):
    """
    Test class that doesn't assert any test, but simply prints all infos regarding a DNS query.
    Prints are executed through 2 tests:

    1- prints infos from the actual dnspython resolver object (RAW INFOS)

    2- prints infos from the DnsResolver object designed in this application

    They can be compared to see if the simplified DnsResolver object of this application is reliable.
    """
    domain_name = None
    dns_resolver = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        cls.domain_name = 'www.netflix.com'
        cls.type = TypesRR.A
        # ELABORATION
        cls.dns_resolver = DnsResolver(True)
        print(f"PARAMETER: {cls.domain_name}")

    def test_1_do_raw_query_and_prints_raw_infos(self):
        print(f"\n------- START TEST 1 -------")
        try:
            answer = self.dns_resolver.resolver.resolve(self.domain_name, self.type.to_string())
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.YXDOMAIN, Exception) as e:  # name is a domain that does not exist
            self.fail(f"!!! {str(e)} !!!")
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
        print(f"------- END TEST 1 -------")

    def test_2_do_query_and_debug_prints_from_application_resolver(self):
        print(f"\n------- START TEST 2 -------")
        try:
            path = self.dns_resolver.do_query(self.domain_name, self.type)
        except (DomainNonExistentError, NoAnswerError, UnknownReasonError) as e:
            self.fail(f"ERROR: {str(e)}")
        print(f"type of path = {type(path)}")
        print(f"canonical name = {path.get_canonical_name()}")
        print(f"resolution = {path.get_resolution()}")
        print(f"path = {path.stamp()}")
        print(f"------- END TEST 2 -------")


if __name__ == '__main__':
    unittest.main()
