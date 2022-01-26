import unittest
from peewee import DoesNotExist
from persistence import helper_script_withdraw, helper_web_site


class ScriptDependenciesErrorSimulationTestCase(unittest.TestCase):
    def test_1_set_web_site_script_withdraw_association_to_null(self):
        print(f"\n------- [1] START SETTING WEB SITE SCRIPT WITHDRAW ASSOCIATION TO NULL QUERY -------")
        # PARAMETERS
        web_site = 'google.it/doodles'
        https = False
        # ELABORATION
        print(f"Web site: {web_site}")
        try:
            wse = helper_web_site.insert(web_site)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        swas = helper_script_withdraw.get_all_of(wse, https)
        for swa in swas:
            swa.delete_instance()
        helper_script_withdraw.insert(wse, None, https, None)
        print(f"------- [1] END SETTING WEB SITE SCRIPT WITHDRAW ASSOCIATION TO NULL QUERY -------")



if __name__ == '__main__':
    unittest.main()
