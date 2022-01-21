from pathlib import Path
from typing import List
from utils import file_utils


def take_temporary_snapshot(web_sites: List[str], mail_domains: List[str], complete_unresolved_database: bool, consider_tld: bool) -> None:
    take_temp_snapshot_of_string_list(web_sites, 'temp_web_pages')
    take_temp_snapshot_of_string_list(mail_domains, 'temp_mail_domains')
    take_temp_snapshot_of_flags(complete_unresolved_database, consider_tld, 'temp_flags')


def take_temp_snapshot_of_string_list(string_list: List[str], filename: str, project_root_directory=Path.cwd()) -> None:
    """
    Export a string list as a .txt file in the SNAPSHOTS folder of the project root folder (PRD) with a predefined
    filename.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is returned.
    If the application is started from a file that belongs to the entities package, then Path.cwd() will return the
    entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set to default as
    if the entry point is main.py file (which is the only entry point considered).
    :param string_list: A list of string.
    :type string_list: List[str]
    :param filename: Name of file without extension.
    :type filename: str
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    """
    file = file_utils.set_file_in_folder("SNAPSHOTS", filename + ".txt",
                                         project_root_directory=project_root_directory)
    with file.open('w', encoding='utf-8') as f:  # 'w' or 'x'
        for string in string_list:
            f.write(string+'\n')
        f.close()


def take_temp_snapshot_of_flags(complete_unresolved_database: bool, consider_tld: bool, filename: str, project_root_directory=Path.cwd()) -> None:
    """
    Export 2 booleans as a .txt file in the SNAPSHOTS folder of the project root folder (PRD) with a predefined
    filename.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is returned.
    If the application is started from a file that belongs to the entities package, then Path.cwd() will return the
    entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set to default as
    if the entry point is main.py file (which is the only entry point considered).
    :param complete_unresolved_database: The complete_unresolved_database flag.
    :type complete_unresolved_database: bool
    :param consider_tld: the consider_tld flag.
    :type consider_tld: bool
    :param filename: Name of file without extension.
    :type filename: str
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    """
    file = file_utils.set_file_in_folder("SNAPSHOTS", filename + ".txt",
                                         project_root_directory=project_root_directory)
    with file.open('w', encoding='utf-8') as f:  # 'w' or 'x'
        f.write('complete_unresolved_database:'+str(complete_unresolved_database)+'\n')
        f.write('consider_tld:'+str(consider_tld))
        f.close()
