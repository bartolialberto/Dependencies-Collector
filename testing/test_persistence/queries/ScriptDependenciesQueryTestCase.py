import unittest
from peewee import DoesNotExist
from persistence import helper_script, helper_script_site, helper_script_server


class ScriptDependenciesQueryTestCase(unittest.TestCase):
    web_site = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.web_site = 'google.it/doodles'
        print(f"PARAMETER = {cls.web_site}")

    def test_1_get_scripts_from_web_site(self):
        print(f"\n------- [1] START GETTING SCRIPTS FROM WEB SITE QUERY -------")
        try:
            ses = helper_script.get_from(self.web_site)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        for i, se in enumerate(ses):
            print(f"script[{i+1}]: src={se.src}")
        print(f"------- [1] END GETTING SCRIPTS FROM WEB SITE QUERY -------")

    def test_2_get_script_sites_from_web_site(self):
        print(f"\n------- [2] START GETTING SCRIPT SITES FROM WEB SITE QUERY -------")
        try:
            sses = helper_script_site.get_from_string_web_site(self.web_site)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        for i, sse in enumerate(sses):
            print(f"script site[{i+1}]: {sse.url.string}")
        print(f"------- [2] END GETTING SCRIPT SITES FROM WEB SITE QUERY -------")

    def test_3_get_script_sites_from_web_site(self):
        print(f"\n------- [3] START GETTING SCRIPT SERVERS FROM WEB SITE QUERY -------")
        try:
            sses = helper_script_server.get_from_string_web_site(self.web_site)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        for i, sse in enumerate(sses):
            if sse is None:
                print(f"script server[{i+1}]: {sse}")
            else:
                print(f"script server[{i+1}]: {sse.name.string}")
        print(f"------- [3] END GETTING SCRIPT SERVERS FROM WEB SITE QUERY -------")


if __name__ == '__main__':
    unittest.main()
