import sqlite3
from typing import Tuple


def get_sqlite_jdbc_version_as_string() -> str:
    """
    The version number of this module, as a string

    :return:
    :rtype: str
    """
    return sqlite3.version


def get_sqlite_jdbc_version() -> Tuple[int, int, int]:
    """
    The version number of this module, as tuple of integers.

    :return:
    :rtype: Tuple[int, int, int]
    """
    return sqlite3.version_info


def get_sqlite_runtime_sqlite_version_as_string() -> str:
    """
    The version number of the run-time SQLite library, as a string.

    :return:
    :rtype: str
    """
    return sqlite3.sqlite_version


def check_jdbc_driver_version() -> bool:
    """
    Checks if the SQLite JDBC driver version is prior to 3.32.0; if it is, False is returned, otherwise True.
    This information is useful when performing multiple insertion in the database.

    :return: True if SQLite JDBC driver version is at least 3.32.0, False otherwise.
    :rtype: bool
    """
    ver = get_sqlite_jdbc_version()
    if ver[0] == 3 and ver[1] < 32:
        return False
    else:
        return True
