import unittest
from peewee import DoesNotExist
from persistence import helper_zone, helper_name_server


class ZoneDependenciesQueryTestCase(unittest.TestCase):
    def test_1_get_dependencies_of_domain_name(self):
        print(f"\n------- [1] START GETTING DEPENDENCIES OF DOMAIN NAME QUERY -------")
        # PARAMETER
        domain_name = 'consent.youtube.com'
        # QUERY
        try:
            zes = helper_zone.get_zone_dependencies_of_string_domain_name(domain_name)
        except DoesNotExist as e:
            self.fail(str(e))
        print(f"Parameter: {domain_name}")
        print(f"Zone dependencies of domain name: {domain_name}")
        for i, ze in enumerate(zes):
            print(f"[{i+1}/{len(zes)}] = {ze.name}")
        print(f"------- [1] END GETTING DEPENDENCIES OF DOMAIN NAME QUERY -------")

    def test_2_get_dependencies_of_zone_name(self):
        print(f"\n------- [2] START GETTING DEPENDENCIES OF ZONE QUERY -------")
        # PARAMETER
        zone_name = 'nstld.com'
        # QUERY
        try:
            zes = helper_zone.get_zone_dependencies_of_zone(zone_name)
        except DoesNotExist as e:
            self.fail(str(e))
        print(f"Parameter: {zone_name}")
        print(f"Zone dependencies of zone: {zone_name}")
        for i, ze in enumerate(zes):
            print(f"[{i+1}/{len(zes)}] = {ze.name}")
        print(f"------- [2] END GETTING DEPENDENCIES OF ZONE QUERY -------")

    def test_3_get_zone_object_from_zone_name(self):
        print(f"\n------- [3] START GETTING ZONE OBJECT FROM ZONE NAME QUERY -------")
        # PARAMETER
        zone_name = 'nstld.com'
        # QUERY
        print(f"Parameter: {zone_name}")
        try:
            zo = helper_zone.get_zone_object_from_zone_name(zone_name)
        except DoesNotExist as e:
            self.fail(str(e))
        print(f"Resolved: {str(zo)}. More prints:")
        for i, name_server in enumerate(zo.nameservers):
            print(f"nameserver[{i+1}/{len(zo.nameservers)}] = {name_server} ===ACCESS_PATH==> {str(zo.resolve_name_server_access_path(name_server).values)}")
        for i, rr in enumerate(zo.aliases):
            print(f"alias[{i+1}/{len(zo.aliases)}] = (name={rr.name}, first_value={rr.get_first_value()})")
        for i, rr in enumerate(zo.addresses):
            print(f"address[{i+1}/{len(zo.addresses)}] = (name={rr.name}, values={str(rr.values)})")
        print(f"------- [3] END GETTING ZONE OBJECT FROM ZONE NAME QUERY -------")

    def test_4_get_all_zones_from_name_server(self):
        print(f"\n------- [4] START GETTING ZONES FROM NAME SERVER QUERY -------")
        # PARAMETER
        name_server = 'av1.nstld.com.'
        # QUERY
        print(f"Parameter: {name_server}")
        try:
            zes = helper_name_server.get_every_zone_of(name_server)
        except DoesNotExist as e:
            self.fail(str(e))
        print(f"Resolved {len(zes)} zones:")
        for i, ze in enumerate(zes):
            print(f"zone[{i+1}/{len(zes)}] = {str(ze)}")
        print(f"------- [4] END GETTING ZONES FROM NAME SERVER QUERY -------")


if __name__ == '__main__':
    unittest.main()
