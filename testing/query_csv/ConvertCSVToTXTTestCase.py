import unittest
from utils import file_utils


class ConvertCSVToTXTTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.csv_filename = 'websites_de'
        cls.new_txt_filename = 'websites_de'
        cls.PRD = file_utils.get_project_root_directory()

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
