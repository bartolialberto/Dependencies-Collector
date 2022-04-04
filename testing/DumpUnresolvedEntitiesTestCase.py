import unittest
from persistence import helper_application_results
from utils import file_utils


class DumpUnresolvedEntitiesTestCase(unittest.TestCase):
    def test_dump(self):
        PRD = file_utils.get_project_root_directory()
        helper_application_results.dump_all_unresolved_entities(PRD, ';')


if __name__ == '__main__':
    unittest.main()
