import os


def parse_file_path(string: str):
    filename, file_extension = os.path.splitext(string)     # extension with the starting point
    return filename, file_extension
