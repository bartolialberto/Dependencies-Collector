import os
import shutil
import time
import traceback
from pathlib import Path
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from utils import file_utils


def take_snapshot(exception: Exception):
    seconds_passed_from_epoch = time.time()
    current_time = time.localtime(seconds_passed_from_epoch)
    # example: executed at 22:10 12/11/2021 ---> folder name: 12112021_2210
    folder_name = f"{current_time.tm_mday:02}{current_time.tm_mon:02}{current_time.tm_year:02}_{current_time.tm_hour:02}{current_time.tm_min:02}{current_time.tm_sec:02}"
    folder = Path(f"{str(Path.cwd())}{os.sep}SNAPSHOTS{os.sep}{folder_name}")
    folder.mkdir(parents=True, exist_ok=False)
    starting_cache_file = Path(f"{str(folder)}{os.sep}starting_cache.csv")
    domain_names_file = Path(f"{str(folder)}{os.sep}domain_names.csv")
    error_file = Path(f"{str(folder)}{os.sep}error.txt")

    # load starting cache
    try:
        result = file_utils.search_for_filename_in_subdirectory("SNAPSHOTS", "temp_cache.csv")
        file = result[0]
        shutil.copy(file, starting_cache_file)
    except FilenameNotFoundError:
        # means that there's no entry in the cache. So we create an empty file
        starting_cache_file.touch()

    # load domain names
    try:
        result = file_utils.search_for_filename_in_subdirectory("SNAPSHOTS", "temp_domain_names.csv")
        file = result[0]
        shutil.copy(file, domain_names_file)
    except FilenameNotFoundError:
        # means that there's no domain names. So we create an empty file
        domain_names_file.touch()

    # write error file
    with open(str(error_file), 'w') as f:  # 'w' or 'x'
        f.write(f"type(Exception): {type(exception)}\n")
        f.write(f"str(Exception): {str(exception)}\n")
        f.write(f"traceback(Exception): {traceback.format_exc()}\n")
        f.close()
