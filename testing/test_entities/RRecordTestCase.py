import unittest
from entities.DomainName import DomainName
from entities.RRecord import RRecord
from entities.enums.TypesRR import TypesRR


class RRecordTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # PARAMETER
        cls.rr = RRecord(
            DomainName('a'),
            TypesRR.NS,
            [
                'b'
            ]
        )
        cls.for_comparison = RRecord(
            DomainName('a'),
            TypesRR.CNAME,
            [
                'b'
            ]
        )

    def test_01_equality(self):
        print(f"\n------- START TEST 1 -------")
        print(f"str of parameter: {str(self.rr)}")
        print(f"str of comparison: {str(self.for_comparison)}")
        self.assertEqual(self.rr, self.for_comparison)
        print(f"------- END TEST 1 -------")

    def test_02_hash(self):
        print(f"\n------- START TEST 2 -------")
        print(f"hash of parameter: {self.rr.__hash__()}")
        print(f"hash of comparison: {self.for_comparison.__hash__()}")
        self.assertEqual(self.rr.__hash__(), self.for_comparison.__hash__())
        # test integrity between __eq__ and __hash__
        self.assertEqual(self.rr.__hash__() == self.for_comparison.__hash__(), self.rr == self.for_comparison)
        print(f"------- END TEST 2 -------")


if __name__ == '__main__':
    unittest.main()
