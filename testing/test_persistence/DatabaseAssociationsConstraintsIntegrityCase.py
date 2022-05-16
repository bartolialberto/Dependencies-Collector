import unittest
from persistence.BaseModel import db, DirectZoneAssociation, DomainNameEntity, WebSiteEntity, WebSiteLandsAssociation, \
    ScriptSiteEntity, ScriptSiteLandsAssociation, IpAddressEntity, IpAddressDependsAssociation, ScriptEntity, \
    ScriptHostedOnAssociation, WebSiteDomainNameAssociation, ScriptSiteDomainNameAssociation, NetworkNumbersAssociation, \
    PrefixesTableAssociation, IpRangeROVEntity, IpRangeTSVEntity


class DatabaseAssociationsConstraintsIntegrityCase(unittest.TestCase):
    def test_01_domain_name_and_direct_zones(self):
        print(f"\n------- START TEST 1 -------")
        domain_names = list()
        direct_zones = list()
        with db.atomic():
            query = DomainNameEntity.select()
            for row in query:
                domain_names.append(row)
        with db.atomic():
            query = DirectZoneAssociation.select()
            for row in query:
                direct_zones.append(row)
        print(f"table {DomainNameEntity._meta.table_name} length={len(domain_names)}")
        print(f"table {DirectZoneAssociation._meta.table_name} length={len(direct_zones)}")
        with db.atomic():
            for domain_name in domain_names:
                result = list()
                query = DirectZoneAssociation.select()\
                    .where(DirectZoneAssociation.domain_name == domain_name)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {domain_name}')
        print(f"------- END TEST 1 -------")

    def test_02_https_websites_and_website_lands(self):
        print(f"\n------- START TEST 2 -------")
        web_sites = list()
        web_site_lands = list()
        with db.atomic():
            query = WebSiteEntity.select()
            for row in query:
                web_sites.append(row)
        with db.atomic():
            query = WebSiteLandsAssociation.select()
            for row in query:
                web_site_lands.append(row)
        print(f"table {WebSiteEntity._meta.table_name} length={len(web_sites)}")
        print(f"table {WebSiteLandsAssociation._meta.table_name} length={len(web_site_lands)}")
        with db.atomic():
            is_https = True
            for web_site in web_sites:
                result = list()
                query = WebSiteLandsAssociation.select()\
                    .where((WebSiteLandsAssociation.web_site == web_site) & (WebSiteLandsAssociation.starting_https == is_https))
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For (HTTPS): {web_site}')
            is_https = False
            for web_site in web_sites:
                result = list()
                query = WebSiteLandsAssociation.select() \
                    .where((WebSiteLandsAssociation.web_site == web_site) & (
                            WebSiteLandsAssociation.starting_https == is_https))
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For (HTTP): {web_site}')
        print(f"------- END TEST 2 -------")

    def test_03_https_scriptsites_and_scriptsite_lands(self):
        print(f"\n------- START TEST 3 -------")
        script_sites = list()
        script_site_lands = list()
        with db.atomic():
            query = ScriptSiteEntity.select()
            for row in query:
                script_sites.append(row)
        with db.atomic():
            query = ScriptSiteLandsAssociation.select()
            for row in query:
                script_site_lands.append(row)
        print(f"table {ScriptSiteEntity._meta.table_name} length={len(script_sites)}")
        print(f"table {ScriptSiteLandsAssociation._meta.table_name} length={len(script_site_lands)}")
        with db.atomic():
            is_https = True
            for script_site in script_sites:
                result = list()
                query = ScriptSiteLandsAssociation.select()\
                    .where((ScriptSiteLandsAssociation.script_site == script_site) & (ScriptSiteLandsAssociation.starting_https == is_https))
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For (HTTPS): {script_site}')
            is_https = False
            for script_site in script_sites:
                result = list()
                query = ScriptSiteLandsAssociation.select() \
                    .where((ScriptSiteLandsAssociation.script_site == script_site) & (
                            ScriptSiteLandsAssociation.starting_https == is_https))
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For (HTTP): {script_site}')
        print(f"\n------- END TEST 3 -------")

    def test_04_ip_address_and_ip_address_depends(self):
        print(f"\n------- START TEST 4 -------")
        ip_addresses = list()
        ip_addresses_depends = list()
        with db.atomic():
            query = IpAddressEntity.select()
            for row in query:
                ip_addresses.append(row)
        with db.atomic():
            query = IpAddressDependsAssociation.select()
            for row in query:
                ip_addresses_depends.append(row)
        print(f"table {IpAddressEntity._meta.table_name} length={len(ip_addresses)}")
        print(f"table {IpAddressDependsAssociation._meta.table_name} length={len(ip_addresses_depends)}")
        with db.atomic():
            for ip_address in ip_addresses:
                result = list()
                query = IpAddressDependsAssociation.select() \
                    .where(IpAddressDependsAssociation.ip_address == ip_address)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {ip_address}')
        print(f"------- END TEST 4 -------")

    def test_05_script_and_script_hosted_on(self):
        print(f"\n------- START TEST 5 -------")
        scripts = list()
        script_hosted_on = list()
        with db.atomic():
            query = ScriptEntity.select()
            for row in query:
                scripts.append(row)
        with db.atomic():
            query = ScriptHostedOnAssociation.select()
            for row in query:
                script_hosted_on.append(row)
        print(f"table {ScriptEntity._meta.table_name} length={len(scripts)}")
        print(f"table {ScriptHostedOnAssociation._meta.table_name} length={len(script_hosted_on)}")
        with db.atomic():
            for script in scripts:
                result = list()
                query = ScriptHostedOnAssociation.select() \
                    .where(ScriptHostedOnAssociation.script == script)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {script}')
        print(f"------- END TEST 5 -------")

    def test_06_website_and_website_domain(self):
        print(f"\n------- START TEST 6 -------")
        web_sites = list()
        web_sites_domain_names = list()
        with db.atomic():
            query = WebSiteEntity.select()
            for row in query:
                web_sites.append(row)
        with db.atomic():
            query = WebSiteDomainNameAssociation.select()
            for row in query:
                web_sites_domain_names.append(row)
        print(f"table {WebSiteEntity._meta.table_name} length={len(web_sites)}")
        print(f"table {WebSiteDomainNameAssociation._meta.table_name} length={len(web_sites_domain_names)}")
        with db.atomic():
            for web_site in web_sites:
                result = list()
                query = WebSiteDomainNameAssociation.select() \
                    .where(WebSiteDomainNameAssociation.web_site == web_site)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {web_site}')
        print(f"------- END TEST 6 -------")

    def test_07_scriptsite_and_scriptsite_domain(self):
        print(f"\n------- START TEST 7 -------")
        script_sites = list()
        script_sites_domain_names = list()
        with db.atomic():
            query = ScriptSiteEntity.select()
            for row in query:
                script_sites.append(row)
        with db.atomic():
            query = ScriptSiteDomainNameAssociation.select()
            for row in query:
                script_sites_domain_names.append(row)
        print(f"table {ScriptSiteEntity._meta.table_name} length={len(script_sites)}")
        print(f"table {ScriptSiteDomainNameAssociation._meta.table_name} length={len(script_sites_domain_names)}")
        with db.atomic():
            for script_site in script_sites:
                result = list()
                query = ScriptSiteDomainNameAssociation.select() \
                    .where(ScriptSiteDomainNameAssociation.script_site == script_site)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {script_site}')
        print(f"------- END TEST 7 -------")

    def test_08_network_numbers(self):
        print(f"\n------- START TEST 8 -------")
        ip_ranges_tsv = list()
        network_numbers = list()
        with db.atomic():
            query = IpRangeTSVEntity.select()
            for row in query:
                ip_ranges_tsv.append(row)
        with db.atomic():
            query = NetworkNumbersAssociation.select()
            for row in query:
                network_numbers.append(row)
        print(f"table {IpRangeTSVEntity._meta.table_name} length={len(ip_ranges_tsv)}")
        print(f"table {NetworkNumbersAssociation._meta.table_name} length={len(network_numbers)}")
        with db.atomic():
            for network in ip_ranges_tsv:
                result = list()
                query = NetworkNumbersAssociation.select() \
                    .where(NetworkNumbersAssociation.ip_range_tsv == network)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {network}')
        print(f"------- END TEST 8 -------")

    def test_09_prefixes_table(self):
        print(f"\n------- START TEST 9 -------")
        ip_ranges_rov = list()
        prefixes_tables = list()
        with db.atomic():
            query = IpRangeROVEntity.select()
            for row in query:
                ip_ranges_rov.append(row)
        with db.atomic():
            query = PrefixesTableAssociation.select()
            for row in query:
                prefixes_tables.append(row)
        print(f"table {IpRangeROVEntity._meta.table_name} length={len(ip_ranges_rov)}")
        print(f"table {PrefixesTableAssociation._meta.table_name} length={len(prefixes_tables)}")
        with db.atomic():
            for network in ip_ranges_rov:
                result = list()
                query = PrefixesTableAssociation.select() \
                    .where(PrefixesTableAssociation.ip_range_rov == network)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {network}')
        print(f"------- END TEST 9 -------")


if __name__ == '__main__':
    unittest.main()
