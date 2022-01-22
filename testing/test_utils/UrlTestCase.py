import unittest

from exceptions.InvalidUrlError import InvalidUrlError
from utils import url_utils


class UrlTestCase(unittest.TestCase):
    def test_correctness(self):
        # PARAMETERS
        url = 'somexyz.com/jquery/ht65.js'
        url = 'https://consent.google.de/ml?continue=https://www.google.de/&gl=IT&m=0&pc=shp&hl=it&src=1'
        # ELABORATION
        is_right = url_utils.is_grammatically_correct(url)
        print(f"URL: {url}")
        print(f"Is that right? {is_right}")
        self.assertTrue(is_right)

    def test_second_component(self):
        # PARAMETERS
        url = 'somexyz.com/jquery/ht65.js'
        url = 'https://consent.google.de/ml?continue=https://www.google.de/&gl=IT&m=0&pc=shp&hl=it&src=1'
        url = 'https://consent.google.de/ml?continue=https://www.google.de/&gl=IT&m=0&pc=shp&hl=it&src=1'
        # ELABORATION
        try:
            second_component = url_utils.deduct_second_component(url)
        except InvalidUrlError as e:
            self.fail(f"!!! {str(e)} !!!")
        print(f"URL: {url}")
        print(f"Second component: {second_component}")

    def test_deduct_http_url(self):
        # PARAMETERS
        as_https = True
        url = 'somexyz.com/jquery/ht65.js'
        url = 'https://consent.google.de/ml?continue=https://www.google.de/&gl=IT&m=0&pc=shp&hl=it&src=1'
        # url = 'consent.google.de/ml?continue=https://www.google.de/&gl=IT&m=0&pc=shp&hl=it&src=1'
        # ELABORATION
        http_url = url_utils.deduct_http_url(url, as_https=as_https)
        print(f"URL: {url}")
        print(f"HTTP URL: {http_url}")


if __name__ == '__main__':
    unittest.main()
