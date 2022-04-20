import unittest
from persistence.BaseModel import db, DirectZoneAssociation, DomainNameEntity, WebSiteEntity, WebSiteLandsAssociation, \
    ScriptSiteEntity, ScriptSiteLandsAssociation, IpAddressEntity, IpAddressDependsAssociation, ScriptEntity, \
    ScriptHostedOnAssociation, WebSiteDomainNameAssociation, ScriptSiteDomainNameAssociation


class DatabaseAssociationsConstraintsCase(unittest.TestCase):
    def test_01_domain_name_and_direct_zones(self):
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
        self.assertEqual(len(domain_names), len(direct_zones))
        with db.atomic():
            for domain_name in domain_names:
                result = list()
                query = DirectZoneAssociation.select()\
                    .where(DirectZoneAssociation.domain_name == domain_name)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {domain_name}')

    def test_02_https_websites_and_website_lands(self):
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
            self.assertEqual(2*len(web_sites), len(web_site_lands))

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

    def test_03_https_scriptsites_and_scriptsite_lands(self):
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
        self.assertEqual(2*len(script_sites), len(script_site_lands))

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

    def test_04_ip_address_and_ip_address_depends(self):
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
        self.assertEqual(len(ip_addresses), len(ip_addresses_depends))
        with db.atomic():
            for ip_address in ip_addresses:
                result = list()
                query = IpAddressDependsAssociation.select() \
                    .where(IpAddressDependsAssociation.ip_address == ip_address)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {ip_address}')

    def test_05_script_and_script_hosted_on(self):
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
        self.assertEqual(len(scripts), len(script_hosted_on))
        with db.atomic():
            for script in scripts:
                result = list()
                query = ScriptHostedOnAssociation.select() \
                    .where(ScriptHostedOnAssociation.script == script)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {script}')

    def test_06_website_and_website_domain(self):
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
        self.assertEqual(len(web_sites), len(web_sites_domain_names))
        with db.atomic():
            for web_site in web_sites:
                result = list()
                query = WebSiteDomainNameAssociation.select() \
                    .where(WebSiteDomainNameAssociation.web_site == web_site)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {web_site}')

    def test_07_scriptsite_and_scriptsite_domain(self):
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
        self.assertEqual(len(script_sites), len(script_sites_domain_names))
        with db.atomic():
            for script_site in script_sites:
                result = list()
                query = ScriptSiteDomainNameAssociation.select() \
                    .where(ScriptSiteDomainNameAssociation.script_site == script_site)
                for row in query:
                    result.append(row)
                self.assertEqual(1, len(result), f'For: {script_site}')


if __name__ == '__main__':
    unittest.main()
