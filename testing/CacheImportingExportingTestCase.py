import os
import unittest
from pathlib import Path
from entities.LocalDnsResolverCache import LocalDnsResolverCache
from entities.RRecord import RRecord
from entities.TypesRR import TypesRR


class CacheImportingExportingTestCase(unittest.TestCase):
    temp_folder = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_folder = Path(f"{str(Path.cwd())}{os.sep}temp")
        cls.temp_folder.mkdir(parents=True, exist_ok=True)

    def setUp(self) -> None:
        self.cache = LocalDnsResolverCache()
        self.cache.add_entry(RRecord("prova1", TypesRR.A, "167.83.69.0"))
        self.cache.add_entry(RRecord("prova2", TypesRR.A, ["144.200.1.34", "199.188.200.1", "94.87.13.4", "13.12.101.1"]))
        self.cache.add_entry(RRecord("prova3", TypesRR.CNAME, ["110.1.34.5", "144.76.9.10"]))
        self.cache.add_entry(RRecord("prova4", TypesRR.NS, "211.34.109.6"))
        self.cache.add_entry(RRecord("prova5", TypesRR.NS, ["213.44.61.100"]))

    def test_export_file(self):
        try:
            self.cache.write_to_csv(str(self.temp_folder)+f"{os.sep}cache.csv")
        except ValueError:
            self.fail("test_export_file() raised ValueError!")
        except PermissionError:
            self.fail("test_export_file() raised PermissionError!")

    def test_import_file(self):
        print("...")
        try:
            self.cache.load_csv(str(self.temp_folder)+f"{os.sep}cache.csv", take_snapshot=False)
        except ValueError:
            self.fail("test_export_file() raised ValueError!")
        except PermissionError:
            self.fail("test_export_file() raised PermissionError!")

    @classmethod
    def tearDownClass(cls) -> None:
        # eseguito alla fine di tutti i test UNA volta
        for file in cls.temp_folder.iterdir():
            file.unlink()
        cls.temp_folder.rmdir()


if __name__ == '__main__':
    unittest.main()
