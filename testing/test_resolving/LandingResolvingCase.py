import unittest
from entities.Url import Url
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.LandingResolver import LandingResolver


class LandingResolvingCase(unittest.TestCase):
    """
    DEFINITIVE TEST

    """
    def setUp(self) -> None:
        # PARAMETERS
        self.sites = {
            # web sites
            Url('google.it/doodles'),
            Url('www.youtube.it/feed/explore'),
            # script sites
            Url('www.youtube.com/s/desktop/5650b92e/jsbin/spf.vflset/spf.js'),
            Url('www.youtube.com/s/player/f93a7034/player_ias.vflset/it_IT/base.js'),
            Url('ssl.google-analytics.com/ga.js')
        }
        # ELABORATION
        dns_resolver = DnsResolver(True)
        resolver = LandingResolver(dns_resolver)
        self.results = resolver.resolve_sites(self.sites)

    def test_01_same_server(self):
        print(f"\n------- START TEST 1 -------")
        for i, url in enumerate(self.results.keys()):
            # HTTPS
            same = (url.domain_name() == self.results[url].https.server)
            print(f"url[{i+1}/{len(self.results.keys())}]: {url} has same server on HTTPS? {same}")
            # HTTP
            same = (url.domain_name() == self.results[url].http.server)
            print(f"\t\t\t{url} has same server on HTTP? {same}")
        print(f"------- END TEST 1 -------")

    def test_02_same_scheme(self):
        print(f"\n------- START TEST 2 -------")
        for i, url in enumerate(self.results.keys()):
            # HTTPS
            same = (True == self.results[url].https.url.is_https())
            print(f"url[{i+1}/{len(self.results.keys())}]: {url} has same landing scheme starting with HTTPS? {same}")
            # HTTP
            same = (True == self.results[url].https.url.is_http())
            print(f"\t\t\t{url} has same landing scheme starting with HTTP? {same}")
        print(f"------- END TEST 2 -------")


if __name__ == '__main__':
    unittest.main()
