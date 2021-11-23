import unittest
from entities.ContentDependenciesResolver import ContentDependencyEntry
from entities.IpAsDatabase import EntryIpAsDatabase, StringEntryIpAsDatabase
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from entities.Zone import Zone
from persistence import helper_domain_name, helper_landing_page, helper_content_dependency, helper_zone, BaseModel, \
    helper_entry_ip_as_database, helper_matches


class DomainNameTest(unittest.TestCase):
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

    def test_domain_name_elaboration_insert(self):
        domain_name = 'google.it'
        zone = Zone('.', [
            RRecord('m.root-servers.net.', TypesRR.A, '202.12.27.33'),
            RRecord('b.root-servers.net.', TypesRR.A, '199.9.14.201'),
            RRecord('g.root-servers.net.', TypesRR.A, '192.112.36.4'),
            RRecord('f.root-servers.net.', TypesRR.A, '192.5.5.241'),
            RRecord('c.root-servers.net.', TypesRR.A, '192.33.4.12'),
            RRecord('a.root-servers.net.', TypesRR.A, '198.41.0.4'),
            RRecord('l.root-servers.net.', TypesRR.A, '199.7.83.42'),
            RRecord('i.root-servers.net.', TypesRR.A, '192.36.148.17'),
            RRecord('d.root-servers.net.', TypesRR.A, '199.7.91.13'),
            RRecord('e.root-servers.net.', TypesRR.A, '192.203.230.10'),
            RRecord('h.root-servers.net.', TypesRR.A, '198.97.190.53'),
            RRecord('k.root-servers.net.', TypesRR.A, '193.0.14.129'),
            RRecord('j.root-servers.net.', TypesRR.A, '192.58.128.30')
        ], [])
        helper_domain_name.insert(domain_name, zone)
        zone = Zone('it.', [
            RRecord('a.dns.it.', TypesRR.A, '194.0.16.215'),
            RRecord('nameserver.cnr.it.', TypesRR.A, '194.119.192.34'),
            RRecord('r.dns.it.', TypesRR.A, '193.206.141.46'),
            RRecord('m.dns.it.', TypesRR.A, '217.29.76.4'),
            RRecord('dns.nic.it.', TypesRR.A, '192.12.192.5'),
            RRecord('s.dns.it.', TypesRR.A, '194.146.106.30')
        ], [])
        helper_domain_name.insert(domain_name, zone)
        zone = Zone('google.it.', [
            RRecord('ns4.google.com.', TypesRR.A, '216.239.38.10'),
            RRecord('ns1.google.com.', TypesRR.A, '216.239.32.10'),
            RRecord('ns2.google.com.', TypesRR.A, '216.239.34.10'),
            RRecord('ns3.google.com.', TypesRR.A, '216.239.36.10')
        ], [])
        helper_domain_name.insert(domain_name, zone)
        zone = Zone('net.', [
            RRecord('l.gtld-servers.net.', TypesRR.A, '192.41.162.30'),
            RRecord('c.gtld-servers.net.', TypesRR.A, '192.26.92.30'),
            RRecord('h.gtld-servers.net.', TypesRR.A, '192.54.112.30'),
            RRecord('g.gtld-servers.net.', TypesRR.A, '192.42.93.30'),
            RRecord('j.gtld-servers.net.', TypesRR.A, '192.48.79.30'),
            RRecord('e.gtld-servers.net.', TypesRR.A, '192.12.94.30'),
            RRecord('b.gtld-servers.net.', TypesRR.A, '192.33.14.30'),
            RRecord('k.gtld-servers.net.', TypesRR.A, '192.52.178.30'),
            RRecord('f.gtld-servers.net.', TypesRR.A, '192.35.51.30'),
            RRecord('d.gtld-servers.net.', TypesRR.A, '192.31.80.30'),
            RRecord('i.gtld-servers.net.', TypesRR.A, '192.43.172.30'),
            RRecord('m.gtld-servers.net.', TypesRR.A, '192.55.83.30'),
            RRecord('a.gtld-servers.net.', TypesRR.A, '192.5.6.30')
        ], [])
        helper_domain_name.insert(domain_name, zone)
        zone = Zone('root-servers.net.', [
            RRecord('l.root-servers.net.', TypesRR.A, '199.7.83.42'),
            RRecord('c.root-servers.net.', TypesRR.A, '192.33.4.12'),
            RRecord('a.root-servers.net.', TypesRR.A, '198.41.0.4'),
            RRecord('g.root-servers.net.', TypesRR.A, '192.112.36.4'),
            RRecord('b.root-servers.net.', TypesRR.A, '199.9.14.201'),
            RRecord('m.root-servers.net.', TypesRR.A, '202.12.27.33'),
            RRecord('j.root-servers.net.', TypesRR.A, '192.58.128.30'),
            RRecord('f.root-servers.net.', TypesRR.A, '192.52.178.30'),
            RRecord('e.root-servers.net.', TypesRR.A, '192.203.230.10'),
            RRecord('i.root-servers.net.', TypesRR.A, '192.36.148.17'),
            RRecord('k.root-servers.net.', TypesRR.A, '193.0.14.129'),
            RRecord('h.root-servers.net.', TypesRR.A, '198.97.190.53'),
            RRecord('d.root-servers.net.', TypesRR.A, '199.7.91.13')
        ], [])
        helper_domain_name.insert(domain_name, zone)
        zone = Zone('dns.it.', [
            RRecord('m.dns.it.', TypesRR.A, '217.29.76.4'),
            RRecord('ns2.nic.it.', TypesRR.A, '192.12.192.3'),
            RRecord('s.dns.it.', TypesRR.A, '194.146.106.30'),
            RRecord('dns.nic.it.', TypesRR.A, '192.12.192.5')
        ], [])
        helper_domain_name.insert(domain_name, zone)

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

    def test_landing_page_insertion(self):
        domain_name = 'google.it'
        landing_page = 'https://google.it/'
        redirection_path = [
            'https://google.it/',
            'https://www.google.it/',
            'https://consent.google.it/ml?continue=https://www.google.it/&gl=IT&m=0&pc=shp&hl=it&src=1'
        ]
        hsts = False
        helper_landing_page.insert(domain_name, landing_page, redirection_path, hsts)

        domain_name = 'youtube.it'
        landing_page = 'https://youtube.it/'
        redirection_path = [
            'https://youtube.it/',
            'https://youtube.com/?gl=IT'
        ]
        hsts = False
        helper_landing_page.insert(domain_name, landing_page, redirection_path, hsts)

    def test_landing_page_querying(self):
        domain_name = 'login.microsoftonline.com'
        domain, redirection_path, hsts = helper_landing_page.get_from_domain_name(domain_name)
        #t = helper_landing_page.get_from_domain_name(domain_name)
        print(f"Landing page, redirection path, hsts associated to domain '{domain_name}' found in the db:")
        for i, page in enumerate(redirection_path):
            print(f"[{i+1}/{len(redirection_path)}] {page}")

    def test_content_dependencies_insertion(self):
        result = {
            'https://www.youtube.com/?gl=IT': [
                ContentDependencyEntry('tracking-protection.cdn.mozilla.net', 'https://tracking-protection.cdn.mozilla.net/ads-track-digest256/94.0/1637071485', 200, 'text/javascript')
            ]
        }
        helper_content_dependency.insert('https://www.youtube.com/?gl=IT', result['https://www.youtube.com/?gl=IT'])

    def test_content_dependencies_query(self):
        list_entries = helper_content_dependency.get_from_landing_page('https://www.youtube.com/?gl=IT')

    def test_entry_ip_as_db_insertion(self):
        nameserver = 'dns.nic.it.'
        entry = EntryIpAsDatabase(StringEntryIpAsDatabase(['192.167.12.3', '192.167.13.0', '1134', 'IT', 'descrip']))
        e = helper_entry_ip_as_database.insert_or_get(entry)
        helper_entry_ip_as_database.populate_matches_association(nameserver, e)

    def test_test(self):
        helper_matches.insert_or_get_only_entry_ip_as_db()

    def tearDown(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()

