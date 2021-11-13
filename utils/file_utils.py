import os
from pathlib import Path
from typing import List, Tuple
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.FilenameNotFoundError import FilenameNotFoundError


def parse_file_path(string: str) -> Tuple[str, str]:
    """
    Split the pathname string into a pair (root, ext) such that root + ext == string, and the extension, ext, is empty
    or begins with a period and contains at most one period.
    If the path contains no extension, ext will be ''.
    If the path contains an extension, then ext will be set to this extension, including the leading period. Note that
    previous periods will be ignored.
    Leading periods on the basename are ignored.
    Example:        'c:/dir' --> ('c:', '/dir')
    Example:        'foo.bar.exe' --> ('foo.bar', '.exe')
    Example:        'C:\\Users\\fabbi\\PycharmProjects\\LavoroTesi\\utils' --> ('C:\\Users\\fabbi\\PycharmProjects\\LavoroTesi\\utils', '')
    Example:        'C:\\Users\\fabbi\\PycharmProjects\\LavoroTesi\\utils\\test.py' --> ('C:\\Users\\fabbi\\PycharmProjects\\LavoroTesi\\utils\\test.py', '.py')

    :param string: The path.
    :type string: str
    :return: A tuple containing the root first and then the extension (with the starting dot).
    :rtype: tuple[str, str]
    """
    filename, file_extension = os.path.splitext(string)     # extension with the starting point
    return filename, file_extension


def parse_file_extension(string: str) -> str:   # with the dot
    """
    Given a path return the extension of the file with the starting dot. In any other case returns ''.

    :param string: The path.
    :type string: str
    :return: The extension with the starting dot. '' is returned if there is not valid file pointed by the string path.
    :rtype: str
    """
    filename, file_extension = parse_file_path(string)
    return file_extension


def search_for_file_type_in_subdirectory(subdirectory_name: str, extension: str, project_root_directory=Path.cwd()) -> List[Path]:   # extension with point
    """
    Given (the correct) path of the project root directory (PRD), this method searches for files of a certain extension
    in a certain subdirectory of the PRD.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is returned.
    If the application is started from a file that belongs to the entities package, then Path.cwd() will return the
    entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set to default as
    if the entry point is main.py file (which is the only entry point considered).

    :param subdirectory_name: The subdirectory name to find.
    :type subdirectory_name: str
    :param extension: The extension of the files interested.
    :type extension: str
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    :raise FileWithExtensionNotFoundError: If such files are absent.
    :return: List of all matched files as Path objects. Impossible to be empty, otherwise the exception is raised.
    :rtype: List[Path]
    """
    result = sorted(project_root_directory.glob(f'{subdirectory_name}/*{extension}'))
    if len(result) == 0:
        raise FileWithExtensionNotFoundError(extension, subdirectory_name)
    else:
        return result       # MEMO: use str(result[index]) to get absolute path of file


def search_for_filename_in_subdirectory(subdirectory_name: str, filename: str, project_root_directory=Path.cwd()) -> List[Path]:   # filename with extension
    """
    Given (the correct) path of the project root directory (PRD), this method searches for files with a certain filename
    in a certain subdirectory of the PRD.
    Path.cwd() returns the current working directory which depends upon the entry
    point of the application; in particular, if we starts the application from the main.py file in the PRD, every time
    Path.cwd() is encountered (even in methods belonging to files that are in sub-folders with respect to PRD) then the
    actual PRD is returned. If the application is started from a file that belongs to the entities package, then
    Path.cwd() will return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD
    parameter is set to default as if the entry point is main.py file (which is the only entry point considered).

    :param subdirectory_name: The subdirectory name to find.
    :type subdirectory_name: str
    :param filename: The filename of the files interested.
    :type filename: str
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    :raise FilenameNotFoundError: If such files are absent.
    :return: List of all matched files as Path objects. Impossible to be empty, otherwise the exception is raised.
    :rtype: List[Path]
    """
    result = sorted(project_root_directory.glob(f'{subdirectory_name}/{filename}'))
    if len(result) == 0:
        raise FilenameNotFoundError(filename, subdirectory_name)
    else:
        return result       # MEMO: use str(result[index]) to get absolute path of file


def set_file_in_folder(subdirectory_name: str, filename: str, project_root_directory=Path.cwd()) -> Path:
    """
    Given (the correct) path of the project root directory (PRD), this method searches for a file with a certain
    filename in a certain subdirectory of the PRD that can be non-existent. The matter is to return the Path object,
    the effective use of this object (read if exists, write the file represented by this path, ...) is up to others.
    If the subdirectory doesn't exists, it will be created automatically.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is returned.
    If the application is started from a file that belongs to the entities package, then Path.cwd() will return the
    entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set to default as
    if the entry point is main.py file (which is the only entry point considered).

    :param subdirectory_name: The subdirectory name to find.
    :type subdirectory_name: str
    :param filename: The filename of the file interested.
    :type filename: str
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    :return: The Path object associated with the parameters.
    :rtype: Path
    """
    for directory in project_root_directory.iterdir():
        if directory.is_dir() and directory.name == subdirectory_name:
            file = Path(f"{str(directory)}{os.sep}{filename}")
            return file
        else:
            pass
    folder = Path(f"{str(Path.cwd())}{os.sep}{subdirectory_name}")
    folder.mkdir(parents=True, exist_ok=False)
    file = Path(f"{str(folder)}{os.sep}{filename}")
    return file


