import unittest
from entities.ContentDependenciesResolver import ContentDependencyEntry
from entities.IpAsDatabase import EntryIpAsDatabase, StringEntryIpAsDatabase
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from entities.Zone import Zone
from persistence import helper_domain_name, helper_landing_page, helper_content_dependency, helper_zone, BaseModel, \
    helper_entry_ip_as_database, helper_matches


class ORMQueryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        # PARAMETERS
        self.rrs = [
            RRecord('b.root-servers.net', TypesRR.A, '199.9.14.201'),
            RRecord('a.dns.it', TypesRR.A, '194.0.16.215'),
            RRecord('nameserver.cnr.it', TypesRR.A, '194.119.192.34'),
            RRecord('e.gtld-servers.net', TypesRR.A, '192.12.94.30'),
            RRecord('j.root-servers.net', TypesRR.A, '192.58.128.30'),
            RRecord('avl.nstld.com', TypesRR.A, '192.42.177.30'),
        ]
        self.zones = [
            Zone('net.', self.rrs[:3], list()),
            Zone('root-servers.net.', self.rrs[3:5], list())
        ]
        self.result = {
            'root-servers.net.': self.zones
        }

        self.urls = [
            'https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#one-to-one',
            'https://www.google.com/search?client=firefox-b-d&q=from+e-r+diagram+creates+sqlalchemy',
            'https://stackoverflow.com/questions/44981986/sqlalchemy-er-diagram-in-python-3/46020917'
        ]

    def test_domain_name_querying(self):
        domain_name = 'pasarela.clave.gob.es'
        zone_list = helper_domain_name.get_zone_dependencies(domain_name)
        print(f"'{domain_name}' dependencies found in the db:")
        for i, zone in enumerate(zone_list):
            print(f"[{i+1}/{len(zone_list)}] {zone.name}")

    def test_zone_query(self):
        zone_name = 'es.'
        zone = helper_zone.get(zone_name)
        print(f"Nameservers associated to zone '{zone_name}' found in the db:")
        for i, nameserver in enumerate(zone.nameservers):
            print(f'[{i+1}/{len(zone.nameservers)}] {nameserver.name} -> {nameserver.get_first_value()}')

    def test_landing_page_querying(self):
        domain_name = 'login.microsoftonline.com'
        domain, redirection_path, hsts = helper_landing_page.get_from_domain_name(domain_name)
        #t = helper_landing_page.get_from_domain_name(domain_name)
        print(f"Landing page, redirection path, hsts associated to domain '{domain_name}' found in the db:")
        for i, page in enumerate(redirection_path):
            print(f"[{i+1}/{len(redirection_path)}] {page}")

    def test_content_dependencies_query(self):
        list_entries = helper_content_dependency.get_from_landing_page('https://www.youtube.com/?gl=IT')


if __name__ == '__main__':
    unittest.main()

