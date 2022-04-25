import unittest
from persistence.BaseModel import db, DirectZoneAssociation, DomainNameEntity, WebSiteEntity, WebSiteLandsAssociation, \
    ScriptSiteEntity, ScriptSiteLandsAssociation, IpAddressEntity, IpAddressDependsAssociation, ScriptEntity, \
    ScriptHostedOnAssociation, WebSiteDomainNameAssociation, ScriptSiteDomainNameAssociation


class DatabaseAssociationsConstraintsIntegrityCase(unittest.TestCase):
    def test_01_domain_name_and_direct_zones(self):
        print(f"\n------- [1] START domain_name VS direct_zone TEST CASE -------")
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
        print(f"------- [1] END domain_name VS direct_zone TEST CASE -------")

    def test_02_https_websites_and_website_lands(self):
        print(f"\n------- [2] START web_site VS web_site_lands TEST CASE -------")
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
        print(f"table {ScriptSiteEntity._meta.table_name} length={len(web_sites)}")
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
        print(f"------- [2] END web_site VS web_site_lands TEST CASE -------")

    def test_03_https_scriptsites_and_scriptsite_lands(self):
        print(f"\n------- [3] START wscript_site VS script_site_lands TEST CASE -------")
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
        print(f"\n------- [3] END script_site VS script_site_lands TEST CASE -------")

    def test_04_ip_address_and_ip_address_depends(self):
        print(f"\n------- [4] START ip_address VS ip_address_depends TEST CASE -------")
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
        print(f"------- [4] END ip_address VS ip_address_depends TEST CASE -------")

    def test_05_script_and_script_hosted_on(self):
        print(f"\n------- [5] START script VS script_hosted_on TEST CASE -------")
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
        print(f"------- [5] END script VS script_hosted_on TEST CASE -------")

    def test_06_website_and_website_domain(self):
        print(f"\n------- [6] START web_site VS web_site_domain_name TEST CASE -------")
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
        print(f"------- [6] END web_site VS web_site_domain_name TEST CASE -------")

    def test_07_scriptsite_and_scriptsite_domain(self):
        print(f"\n------- [7] START script_site VS script_site_domain_name TEST CASE -------")
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
        print(f"------- [7] END script_site VS script_site_domain_name TEST CASE -------")


if __name__ == '__main__':
    unittest.main()
