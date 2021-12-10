import ipaddress
import unittest
from entities.ContentDependenciesResolver import ContentDependencyEntry
from entities.IpAsDatabase import EntryIpAsDatabase, StringEntryIpAsDatabase
from entities.ROVPageScraper import RowPrefixesTable
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from entities.Zone import Zone
from persistence import helper_domain_name, helper_landing_page, helper_content_dependency,\
    helper_entry_ip_as_database, helper_matches


class ORMInsertionTestCase(unittest.TestCase):
    def test_insertion_domain_name(self):
        print(f"test_insertion_domain_name ****************************************************************")
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


    def test_multiple_insertions_domain_names(self):
        print(f"test_multiple_insertions_domain_names ****************************************************************")
        dns_results = {
            'login.microsoftonline.com': [
                Zone('dns.it.', [
                    RRecord('m.dns.it.', TypesRR.A, '217.29.76.4'),
                    RRecord('ns2.nic.it.', TypesRR.A, '192.12.192.3'),
                    RRecord('s.dns.it.', TypesRR.A, '194.146.106.30'),
                    RRecord('dns.nic.it.', TypesRR.A, '192.12.192.5')
                ], []),
                Zone('root-servers.net.', [
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
                ], []),
                Zone('net.', [
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
            ],
            'auth.digidentity.eu': [
                Zone('google.it.', [
                    RRecord('ns4.google.com.', TypesRR.A, '216.239.38.10'),
                    RRecord('ns1.google.com.', TypesRR.A, '216.239.32.10'),
                    RRecord('ns2.google.com.', TypesRR.A, '216.239.34.10'),
                    RRecord('ns3.google.com.', TypesRR.A, '216.239.36.10')
                ], [])
            ],
            'google.it': [
                Zone('it.', [
                    RRecord('a.dns.it.', TypesRR.A, '194.0.16.215'),
                    RRecord('nameserver.cnr.it.', TypesRR.A, '194.119.192.34'),
                    RRecord('r.dns.it.', TypesRR.A, '193.206.141.46'),
                    RRecord('m.dns.it.', TypesRR.A, '217.29.76.4'),
                    RRecord('dns.nic.it.', TypesRR.A, '192.12.192.5'),
                    RRecord('s.dns.it.', TypesRR.A, '194.146.106.30')
                ], []),
                Zone('google.it.', [
                    RRecord('ns4.google.com.', TypesRR.A, '216.239.38.10'),
                    RRecord('ns1.google.com.', TypesRR.A, '216.239.32.10'),
                    RRecord('ns2.google.com.', TypesRR.A, '216.239.34.10'),
                    RRecord('ns3.google.com.', TypesRR.A, '216.239.36.10')
                ], [])
            ]
        }
        helper_domain_name.multiple_inserts(dns_results)

    def test_insertion_landing_page_result(self):
        print(f"test_insertion_landing_page_result ****************************************************************")
        domain_name = 'youtube.it'
        landing_page = 'https://youtube.it/'
        redirection_path = [
            'https://youtube.it/',
            'https://youtube.com/?gl=IT'
        ]
        hsts = False
        helper_landing_page.insert(domain_name, landing_page, redirection_path, hsts)

    def test_multiple_inserts_landing_page_results(self):
        print(f"test_multiple_inserts_landing_page_results ****************************************************************")
        # Format
        # landing_page_results = dict with domain name as key
        # value of a key is a tuple of 3 elements: (landing_url as string, redirection path as a list of string, if it is hsts as boolean)
        landing_page_results = {
            'google.it': (
                'https://google.it/',
                [
                    'https://google.it/',
                    'https://www.google.it/',
                    'https://consent.google.it/ml?continue=https://www.google.it/&gl=IT&m=0&pc=shp&hl=it&src=1'
                ],
                False
            ),
            'auth.digidentity.eu': (
                'https://auth.digidentity.eu/',
                [
                    'https://auth.digidentity.eu/'
                ],
                False
            )
        }
        helper_landing_page.multiple_inserts(landing_page_results)

    def test_insertion_content_dependencies_result(self):
        print(f"test_insertion_content_dependencies_result ****************************************************************")
        result = [
            ContentDependencyEntry('tracking-protection.cdn.mozilla.net', 'https://tracking-protection.cdn.mozilla.net/ads-track-digest256/94.0/1637071485', 200, 'text/javascript')
        ]
        helper_content_dependency.insert('https://www.youtube.com/?gl=IT', result)

    def test_multiple_insertions_content_dependencies_results(self):
        print(f"test_multiple_insertions_content_dependencies_results ****************************************************************")
        results = {
            'https://www.youtube.com/?gl=IT': [
                ContentDependencyEntry('tracking-protection.cdn.mozilla.net', 'https://tracking-protection.cdn.mozilla.net/ads-track-digest256/94.0/1637071485', 200, 'text/javascript')
            ]
        }
        helper_content_dependency.multiple_inserts(results)

    def test_entry_ip_as_db_insertion(self):
        print(f"test_entry_ip_as_db_insertion ****************************************************************")
        nameserver = 'dns.nic.it.'
        entry = EntryIpAsDatabase(StringEntryIpAsDatabase(['192.167.12.3', '192.167.13.0', '1134', 'IT', 'descrip']))
        e = helper_entry_ip_as_database.insert(entry)
        helper_entry_ip_as_database.populate_matches_association(nameserver, e)

    def test_insertion_all_entries(self):
        print(f"test_insertion_all_entries ****************************************************************")
        all_entries_result_by_as = {
            10886: {
                'd.root-servers.net': [
                    '199.7.91.13',
                    EntryIpAsDatabase(StringEntryIpAsDatabase(['38.124.249.0', '38.124.249.255', '10886', 'US', 'MAX-GIGAPOP - University of Maryland'])),
                    ipaddress.IPv4Network('199.7.91.0/24'),
                    RowPrefixesTable('10886', '199.7.91.13/24', '65536', 'IT', '9', 'VLD', '[Addr:150.217.0.0/16,Max:16,AS:137]')
                ]
            }
        }
        helper_matches.insert_all_entries_associated(all_entries_result_by_as)


if __name__ == '__main__':
    unittest.main()

