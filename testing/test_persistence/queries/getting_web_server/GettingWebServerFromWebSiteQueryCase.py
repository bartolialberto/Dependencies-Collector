import unittest
from entities.Url import Url
from persistence import helper_web_site, helper_web_server


class GettingWebServerFromWebSiteQueryCase(unittest.TestCase):
    http_server = None
    https_server = None
    wse = None
    web_site_url = None

    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.web_site_url = Url('www.netflix.com/it-en/login')
        # QUERY
        cls.wse = helper_web_site.get(cls.web_site_url)
        cls.https_server, cls.http_server = helper_web_server.get_from(cls.wse)
        print(f"Web site: {cls.web_site_url} ==> HTTPS: {cls.https_server.name.string}, HTTP: {cls.http_server.name.string}")
        starting_https_server = helper_web_server.get_of(cls.wse, True)
        print(f"Web site: {cls.web_site_url} + starting_https: {True} ==> {starting_https_server.name.string}")
        starting_http_server = helper_web_server.get_of(cls.wse, False)
        print(f"Web site: {cls.web_site_url} + starting_https: {False} ==> {starting_http_server.name.string}")

    def test_01_from_web_server(self):
        print(f"\n------- [1] START QUERY -------")
        # HTTPS
        wses = helper_web_site.get_of(self.https_server)
        str_wses = set(map(lambda wse: wse.url.string, wses))
        print(f"From HTTPS: {self.https_server.name.string} ==> {str(str_wses)}")
        self.assertIn(self.web_site_url.second_component(), str_wses)

        # HTTP
        wses = helper_web_site.get_of(self.http_server)
        str_wses = set(map(lambda wse: wse.url.string, wses))
        print(f"From HTTP: {self.http_server.name.string} ==> {str(str_wses)}")
        self.assertIn(self.web_site_url.second_component(), str_wses)
        print(f"------- [1] END QUERY -------")


if __name__ == '__main__':
    unittest.main()
