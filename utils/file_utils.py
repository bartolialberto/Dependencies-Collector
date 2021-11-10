import os
from pathlib import Path
from typing import List
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.FilenameNotFoundError import FilenameNotFoundError


# filename: tutto il percorso meno che l'estensione (col nome del file)
# file_extension: extension with the starting point
from utils import domain_name_utils
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


def search_for_file_type_in_subdirectory(root_directory: Path, subdirectory_name: str, extension: str) -> List[Path]:   # extension with point
    result = sorted(root_directory.glob(f'{subdirectory_name}/*{extension}'))
    if len(result) == 0:
        raise FileWithExtensionNotFoundError(extension, subdirectory_name)
    else:
        return result       # MEMO: use str(result[index]) to get absolute path of file


def search_for_filename_in_subdirectory(root_directory: Path, subdirectory_name: str, filename: str) -> List[Path]:   # filename with extension
    result = sorted(root_directory.glob(f'{subdirectory_name}/{filename}'))
    if len(result) == 0:
        raise FilenameNotFoundError(filename, subdirectory_name)
    else:
        return result       # MEMO: use str(result[index]) to get absolute path of file


def set_file_in_folder(project_root_directory: Path, folder_name: str, filename: str):
    for directory in project_root_directory.cwd().iterdir():
        if directory.is_dir() and directory.name == folder_name:
            folder = directory
            file = Path(f"{str(folder)}{os.sep}{filename}")
            return file
        else:
            folder = Path(f"{str(project_root_directory)}{os.sep}{folder_name}")
            folder.mkdir(parents=True, exist_ok=False)
            file = Path(f"{str(folder)}{os.sep}{filename}")
            return file


