import unittest
from pathlib import Path
from persistence.BaseModel import project_root_directory_name


class ConvertCSVToTXTTestCase(unittest.TestCase):
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
        cls.csv_filename = 'websites_us'
        cls.new_txt_filename = 'websites_us'

    def test_conversion(self):
        new_lines = list()
        f = open(str(self.csv_filename+".csv"), "r")
        for line in f:
            if line.startswith('www.'):
                new_lines.append(line[4:])
            else:
                new_lines.append(line)
        f.close()

        f = open(str(self.new_txt_filename+".txt"), "r")
        for line in f:
            f.write(line)
        f.close()


if __name__ == '__main__':
    unittest.main()
