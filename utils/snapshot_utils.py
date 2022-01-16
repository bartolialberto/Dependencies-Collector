import csv
from pathlib import Path
from typing import List
from utils import file_utils


def take_temporary_snapshot(web_sites: List[str], script_sites: List[str], persist_errors: bool, consider_tld: bool) -> None:
    take_temp_snapshot_of_string_list(web_sites, 'temp_web_sites')
    take_temp_snapshot_of_string_list(script_sites, 'temp_script_sites')
    take_temp_snapshot_of_flags(persist_errors, consider_tld, 'temp_flags')


def take_temp_snapshot_of_string_list(domain_name_list: List[str], filename: str, project_root_directory=Path.cwd()) -> None:
    """
    Export a string list as a .csv file in the SNAPSHOTS folder of the project root folder (PRD) with a predefined
    filename.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is returned.
    If the application is started from a file that belongs to the entities package, then Path.cwd() will return the
    entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set to default as
    if the entry point is main.py file (which is the only entry point considered).


    :param domain_name_list: A list of domain name.
    :type domain_name_list: List[str]
    :param filename: Name of file without extension.
    :type filename: str
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    """
    file = file_utils.set_file_in_folder("SNAPSHOTS", filename + ".csv",
                                         project_root_directory=project_root_directory)
    with file.open('w', encoding='utf-8', newline='') as f:
        write = csv.writer(f)
        for domain_name in domain_name_list:
            write.writerow([domain_name])
        f.close()


def take_temp_snapshot_of_flags(persist_errors: bool, consider_tld: bool, filename: str, project_root_directory=Path.cwd()) -> None:
    """
    Export 2 booleans as a .csv file in the SNAPSHOTS folder of the project root folder (PRD) with a predefined
    filename.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is returned.
    If the application is started from a file that belongs to the entities package, then Path.cwd() will return the
    entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set to default as
    if the entry point is main.py file (which is the only entry point considered).


    :param persist_errors: The persist_errors flag.
    :type persist_errors: bool
    :param consider_tld: the consider_tld flag.
    :type consider_tld: bool
    :param filename: Name of file without extension.
    :type filename: str
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    """
    file = file_utils.set_file_in_folder("SNAPSHOTS", filename + ".csv",
                                         project_root_directory=project_root_directory)
    with file.open('w', encoding='utf-8', newline='') as f:
        write = csv.writer(f)
        write.writerow(['persist_errors', persist_errors])
        write.writerow(['consider_tld', consider_tld])
        f.close()
