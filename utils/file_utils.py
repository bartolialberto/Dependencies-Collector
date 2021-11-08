import os


# filename: tutto il percorso meno che l'estensione (col nome del file)
# file_extension: extension with the starting point
def parse_file_path(string: str) -> (str, str):
    filename, file_extension = os.path.splitext(string)     # extension with the starting point
    return filename, file_extension


def parse_file_extension(string: str) -> str:   # with the dot
    filename, file_extension = parse_file_path(string)
    return file_extension


def parse_filename(path: str):
    filepath, file_extension = parse_file_path(path)
    index = None
    try:
        index = filepath.rindex('\\')
    except ValueError:
        try:
            index = filepath.rindex('/')
        except ValueError:
            index = -1      # considering +1 after
    finally:
        return filepath[index+1:]