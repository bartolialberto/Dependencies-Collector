import unittest
from pathlib import Path
from persistence.BaseModel import project_root_directory_name
from utils import file_utils


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
        cls.PRD = ConvertCSVToTXTTestCase.get_project_root_folder()

    def test_conversion(self):
        new_lines = list()
        input_file = file_utils.set_file_in_folder('input', self.csv_filename+".csv", self.PRD)
        f_in = open(str(input_file), "r")
        for line in f_in:
            if line.startswith('www.'):
                new_lines.append(line[4:])
            else:
                new_lines.append(line)
        f_in.close()

        new_file = file_utils.set_file_in_folder('output', self.new_txt_filename + ".txt", self.PRD)
        with open(str(new_file), "w") as f_out:
            for line in new_lines:
                f_out.write(line)
            f_out.close()


if __name__ == '__main__':
    unittest.main()
