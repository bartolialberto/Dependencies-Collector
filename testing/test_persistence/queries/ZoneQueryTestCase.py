import unittest
from peewee import DoesNotExist
from persistence import helper_zone


class ZoneQueryTestCase(unittest.TestCase):
    def test_1_resolving_zone_object_from_zone_name(self):
        print(f"\n------- [1] START RESOLVING ZONE OBJECT FROM ZONE NAME QUERY -------")
        # PARAMETER
        zone_name = 'cdn-auth.digidentity.eu'
        # QUERY
        print(f"Parameter: {zone_name}")
        try:
            zo, aliases_dne = helper_zone.resolve_zone_object(zone_name)
        except DoesNotExist as e:
            self.fail(str(e))
        print(f"Name resolution path: {zo.stamp_zone_name_resolution_path()}")
        print(f"Resolved: {str(zo)}. More prints:")
        for i, name_server in enumerate(zo.nameservers):
            print(f"nameserver[{i+1}/{len(zo.nameservers)}]: {zo.stamp_access_path(name_server)}")
        print(f"------- [1] START RESOLVING ZONE OBJECT FROM ZONE NAME QUERY -------")

    def test_2_getting_zone_object_from_zone_name(self):
        print(f"\n------- [2] START GETTING ZONE OBJECT FROM ZONE NAME QUERY -------")
        # PARAMETER
        zone_name = 'cdn-auth.digidentity.eu'
        # QUERY
        print(f"Parameter: {zone_name}")
        try:
            zo, aliases_dne = helper_zone.get_zone_object_from_zone_name(zone_name)
        except DoesNotExist as e:
            self.fail(str(e))
        print(f"Resolved: {str(zo)}. More prints:")
        for i, name_server in enumerate(zo.nameservers):
            print(f"nameserver[{i+1}/{len(zo.nameservers)}]: {zo.stamp_access_path(name_server)}")
        print(f"------- [2] START GETTING ZONE OBJECT FROM ZONE NAME QUERY -------")


if __name__ == '__main__':
    unittest.main()
