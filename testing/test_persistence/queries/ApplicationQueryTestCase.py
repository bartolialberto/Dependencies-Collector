import unittest

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

    def test_3_query_zone_object_from_web_site(self):
        print(f"\n------- [3] START GETTING ZONE OBJECT FROM WEB SITE QUERY -------")
        # PARAMETER
        web_site = 'www.youtube.com/feed/explore'
        # QUERY
        print(f"Parameter: web site = {web_site}")
        zo = helper_application_queries.get_direct_zone_from_web_site(web_site)
        print(f"Direct zone name: {zo.name}")
        for i, name_server in enumerate(zo.nameservers):
            try:
                ip_access_path = zo.resolve_name_server_access_path(name_server)
                print(f"Direct zone name server[{i + 1}]: {name_server} --> {str(ip_access_path.values)}")
            except NoAvailablePathError:
                print(f"Direct zone name server[{i+1}]: {name_server} --> HAS NO ACCESS PATH")

        print(f"------- [3] END GETTING ZONE OBJECT FROM WEB SITE QUERY -------")


if __name__ == '__main__':
    unittest.main()
