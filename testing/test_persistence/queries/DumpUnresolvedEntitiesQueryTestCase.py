import unittest
from persistence import helper_application_results


class DumpUnresolvedEntitiesQueryTestCase(unittest.TestCase):
    def test_getting_unresolved_entities(self):
        results = helper_application_results.get_unresolved_entities()
        for i, res in enumerate(results):
            print(f"entity[{i+1}/{len(results)}]")
            print(f"---> entity: type={type(res.entity)}, str={str(res.entity)}")
            print(f"---> cause: str={str(res.cause)}")
            print(f"---> entity_cause: type={type(res.entity_cause)}, str={str(res.entity_cause)}")


if __name__ == '__main__':
    unittest.main()
