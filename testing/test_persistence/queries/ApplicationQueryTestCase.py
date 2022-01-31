import unittest
from peewee import DoesNotExist
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_application_queries


class ApplicationQueryTestCase(unittest.TestCase):
    def test_1_query_all_zone_dependencies_of_a_web_site(self):
        print(f"\n------- [1] START GETTING ALL ZONE DEPENDENCIES OF WEB SITE QUERY -------")
        # PARAMETER (either URL or HTTP URL)
        web_site = 'www.youtube.it/feed/explore'
        # QUERY
        print(f"Parameter: web site = {web_site}")
        zes = helper_application_queries.get_all_zone_dependencies_from_web_site(web_site)
        for i, ze in enumerate(zes):
            print(f"zone dependency[{i + 1}]: {str(ze.name)}")
        print(f"------- [1] END GETTING ALL ZONE DEPENDENCIES OF WEB SITE QUERY -------")

    def test_2_query_all_web_sites_which_depends_upon_a_zone(self):
        print(f"\n------- [2] START GETTING ALL WEB SITES THAT DEPENDS ON ZONE QUERY -------")
        # PARAMETER
        zone_name = 'youtube.com'
        # QUERY
        print(f"Parameter: zone name = {zone_name}")
        wses = helper_application_queries.get_all_web_sites_from_zone_name(zone_name)
        for i, wse in enumerate(wses):
            print(f"web site[{i + 1}]: {str(wse.url.string)}")
        print(f"------- [2] END GETTING ALL WEB SITES THAT DEPENDS ON ZONE QUERY -------")

    def test_3_query_direct_zone_object_from_web_site(self):
        print(f"\n------- [3] START GETTING DIRECT ZONE OBJECT FROM WEB SITE QUERY -------")
        # PARAMETER
        web_site = 'www.youtube.com/feed/explore'
        # QUERY
        print(f"Parameter: web site = {web_site}")
        zo = helper_application_queries.get_direct_zone_from_web_site(web_site)
        print(f"Direct zone name: {zo.name}")
        for i, name_server in enumerate(zo.nameservers):
            try:
                print(f"Direct zone name server[{i + 1}]: {zo.stamp_access_path(name_server)}")
            except NoAvailablePathError:
                print(f"Direct zone name server[{i+1}]: {name_server} --> HAS NO ACCESS PATH")
        print(f"------- [3] END GETTING DIRECT ZONE OBJECT FROM WEB SITE QUERY -------")

    def test_4_query_all_autonomous_systems_from_a_zone_name(self):
        print(f"\n------- [4] START GETTING AUTONOMOUS SYSTEM FROM ZONE NAME QUERY -------")
        # PARAMETER
        zone_name = 'nstld.com'
        # QUERY
        print(f"Parameter: zone name = {zone_name}")
        try:
            ases = helper_application_queries.get_autonomous_systems_dependencies_from_zone_name(zone_name)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        for i, ase in enumerate(ases):
            print(f"autonomous system[{i+1}]: AS{ase.number}\t{ase.description}")
        print(f"------- [4] END GETTING AUTONOMOUS SYSTEM FROM ZONE NAME QUERY -------")

    def test_5_query_all_zone_names_from_autonomous_system_number(self):
        print(f"\n------- [5] START GETTING ZONE NAMES FROM AUTONOMOUS SYSTEM QUERY -------")
        # PARAMETER
        autonomous_system_number = 10515
        # QUERY
        print(f"Parameter: AS number = {autonomous_system_number}")
        try:
            zes = helper_application_queries.get_zone_names_dependencies_from_autonomous_system(autonomous_system_number)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        for i, ze in enumerate(zes):
            print(f"zone[{i+1}]: {ze.name}")
        print(f"------- [5] END GETTING ZONE NAMES FROM AUTONOMOUS SYSTEM QUERY -------")


if __name__ == '__main__':
    unittest.main()
