import unittest
from peewee import DoesNotExist
from entities.Url import Url
from persistence import helper_web_site, helper_web_site_lands, helper_script_site, helper_script_site_lands


class LandingErrorCase(unittest.TestCase):
    def test_01_set_web_site_lands_association_to_null(self):
        print(f"\n------- START TEST 1 -------")
        # PARAMETERS
        web_site = Url('google.it/doodles')
        https = False
        # ELABORATION
        print(f"Web site: {web_site}")
        try:
            wse = helper_web_site.get(web_site)
        except DoesNotExist:
            wse = helper_web_site.insert(web_site)
        wslas = helper_web_site_lands.get_all_from_entity_web_site_and_scheme(wse, https)
        for wsla in wslas:
            wsla.delete_instance()
        helper_web_site_lands.insert(wse, https, None, None)
        print(f"------- END TEST 1 -------")

    def test_02_set_script_site_lands_association_to_null(self):
        print(f"\n------- START TEST 2 -------")
        # PARAMETERS
        script_site = Url('www.google.com/doodles/js/slashdoodles__it.js')
        https = True
        # ELABORATION
        print(f"Script site: {script_site}")
        try:
            sse = helper_script_site.get(script_site)
        except DoesNotExist:
            sse = helper_script_site.insert(script_site)
        sslas = helper_script_site_lands.get_all_from_entity_script_site_and_scheme(sse, https)
        for ssla in sslas:
            ssla.delete_instance()
        helper_script_site_lands.insert(sse, https, None, None)
        print(f"------- END TEST 2 -------")


if __name__ == '__main__':
    unittest.main()
