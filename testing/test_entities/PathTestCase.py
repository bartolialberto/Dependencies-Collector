import unittest
from entities.RRecord import RRecord
from entities.paths.builders import APathBuilder


class PathTestCase(unittest.TestCase):
    def test_something(self):
        ap = APathBuilder()
        ap.add_cname(RRecord())


if __name__ == '__main__':
    unittest.main()
