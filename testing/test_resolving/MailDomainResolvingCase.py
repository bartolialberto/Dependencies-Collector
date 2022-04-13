import unittest
from entities.DomainName import DomainName
from entities.enums.TypesRR import TypesRR
from entities.resolvers.DnsResolver import DnsResolver
from utils import file_utils


class MailDomainResolvingCase(unittest.TestCase):
    """
    DEFINITIVE TEST

    """
    domain_names = None
    dns_resolver = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETERS
        domain_name_strings = ['pec.comune.bologna.it']
        cls.cache_filename = 'cache_from_dns_test'
        cls.error_logs_filename = 'error_logs_from_test'
        # ELABORATION
        cls.domain_names = DomainName.from_string_list(domain_name_strings)
        cls.PRD = file_utils.get_project_root_directory()
        cls.dns_resolver = DnsResolver(True)
        cls.dns_resolver.cache.clear()
        print("START RESOLVING")
        cls.results = cls.dns_resolver.resolve_multiple_mail_domains(cls.domain_names)
        print("END RESOLVING")

    def test_01_control_results(self):
        print(f"\n------- [1] START CONTROL RESULTS TEST -------")
        for i, mail_domain in enumerate(self.results.dependencies.keys()):
            print(f"mail domain[{i+1}/{len(self.results.dependencies.keys())}]: {mail_domain}")
            mail_servers = set()
            mx_path = self.dns_resolver.do_query(mail_domain.string, TypesRR.MX)
            for j, ms in enumerate(mx_path.get_resolution().values):
                print(f"from query[{j+1}/{len(mx_path.get_resolution().values)}] = {ms}")
                mail_servers.add(ms)

            qnames = set()
            for j, mail_server in enumerate(self.results.dependencies[mail_domain].mail_servers_paths.keys()):
                print(f"from result[{j + 1}/{len(self.results.dependencies[mail_domain].mail_servers_paths.keys())}] = {mail_server}")
                qnames.add(mail_server)
            self.assertSetEqual(mail_servers, qnames)
        print(f"------- [1] END CONTROL RESULTS TEST -------")


if __name__ == '__main__':
    unittest.main()
