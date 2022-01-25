import unittest
from pathlib import Path
from entities.DatabaseEntitiesCompleter import DatabaseEntitiesCompleter
from persistence import helper_application_results
from persistence.BaseModel import project_root_directory_name


class DumpUnresolvedEntitiesTestCase(unittest.TestCase):
    @staticmethod
    def get_project_root_folder() -> Path:
        current = Path.cwd()
        while True:
            if current.name == project_root_directory_name:
                return current
            else:
                current = current.parent

    @classmethod
    def setUpClass(cls) -> None:
        cls.PRD = DumpUnresolvedEntitiesTestCase.get_project_root_folder()

    def test_1_dump_unresolved_entities(self):
        print(f"\n------- [1] START DUMPING UNRESOLVED ENTITIES TEST -------")
        unresolved_entities = helper_application_results.get_unresolved_entities()
        DatabaseEntitiesCompleter.dump_unresolved_entities(unresolved_entities, ';', project_root_directory=self.PRD)
        print(f"------- [1] END DUMPING UNRESOLVED ENTITIES TEST -------")


if __name__ == '__main__':
    unittest.main()
