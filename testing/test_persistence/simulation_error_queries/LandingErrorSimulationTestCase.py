import unittest
from peewee import DoesNotExist
from persistence import helper_web_site, helper_web_site_lands, helper_script_site, helper_script_site_lands


class LandingErrorSimulationTestCase(unittest.TestCase):
    def test_1_set_web_site_lands_association_to_null(self):
        print(f"\n------- [1] START SETTING WEB SITE LANDING ASSOCIATION TO NULL QUERY -------")
        # PARAMETERS
        web_site = 'google.it/doodles'
        https = False
        # ELABORATION
        print(f"Web site: {web_site}")
        try:
            wse = helper_web_site.insert(web_site)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        wslas = helper_web_site_lands.get_all_from_entity_web_site_and_scheme(wse, https)
        for wsla in wslas:
            wsla.delete_instance()
        helper_web_site_lands.insert(wse, None, https)
        print(f"------- [1] END SETTING WEB SITE LANDING ASSOCIATION TO NULL QUERY -------")

    def test_2_set_script_site_lands_association_to_null(self):
        print(f"\n------- [2] START SETTING SCRIPT SITE LANDING ASSOCIATION TO NULL QUERY -------")
        # PARAMETERS
        script_site = 'www.google.com/doodles/js/slashdoodles__it.js'
        https = True
        # ELABORATION
        print(f"Script site: {script_site}")
        try:
            sse = helper_script_site.insert(script_site)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        sslas = helper_script_site_lands.get_all_from_entity_script_site_and_scheme(sse, https)
        for ssla in sslas:
            ssla.delete_instance()
        helper_script_site_lands.insert(sse, None, https)
        print(f"------- [2] END SETTING SCRIPT SITE LANDING ASSOCIATION TO NULL QUERY -------")


if __name__ == '__main__':
    unittest.main()
