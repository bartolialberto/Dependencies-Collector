import unittest

from persistence import helper_prefixes_table


class ASAndROVRelationQueryTestCase(unittest.TestCase):
    def test_1_get_all_from_as(self):
        print(f"\n------- [1] START GETTING ALL NETWORKS FORM AS NUMBER -------")
        # PARAMETER
        as_number = '137'
        # QUERY
        # helper_prefixes_table.get_all_from()
        print(f"------- [1] END GETTING ALL NETWORKS FORM AS NUMBER -------")


if __name__ == '__main__':
    unittest.main()
