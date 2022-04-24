import ipaddress
from typing import Tuple, List
from entities.SchemeUrl import SchemeUrl
from entities.Url import Url
import os
from pathlib import Path
import requests
import gzip
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from static_variables import INPUT_FOLDER_NAME, IP_ASN_ARCHIVE_NAME
from utils import file_utils


def resolve_landing_page(url: Url, as_https=True) -> Tuple[SchemeUrl, List[str], bool, ipaddress.IPv4Address]:
    """
    This method returns the landing page, the redirection path, the Strict Transport Security validity from an HTTP URL.
    In particular it creates an url from the string parameter and then tries a GET HTTP method with it.

    :param string: A string.
    :type string: str
    :param as_https: A boolean setting if the url constructed from the domain name parameter uses HTTPS or HTTP.
    :type as_https: bool
    :raise requests.exceptions.ConnectTimeout: The request timed out while trying to connect to the remote server.
    Requests that produced this error are safe to retry.
    :raise requests.exceptions.ConnectionError: A Connection error occurred. This occurs if https is not supported by
    the server.
    :raise requests.exceptions.URLRequired: A valid URL is required to make a request.
    :raise requests.exceptions.TooManyRedirects: Too many redirects.
    :raise requests.exceptions.ReadTimeout: The server did not send any data in the allotted amount of time.
    :raise requests.exceptions.Timeout: The request timed out. Catching this error will catch both ConnectTimeout and
    ReadTimeout errors.
    :raise requests.exceptions.RequestException: There was an ambiguous exception that occurred while handling your
    :return: A tuple containing the landing url, all the url redirection and the HSTS validity.
    :rtype: Tuple[str, List[str], bool, ipaddress.IPv4Address]
    """
    redirection_path = list()
    if as_https:
        url_string = url.https().string
    else:
        url_string = url.http().string
    try:
        response = requests.get(url_string, headers={'Connection': 'close'}, stream=True)
        # tmp = response.raw._connection.sock.getsockname()
        # tmp = response.raw._connection.sock.getpeername()
        tmp = response.raw._fp.fp.raw._sock.getpeername()
        ip_string = response.raw._fp.fp.raw._sock.getpeername()[0]
        port_string = response.raw._fp.fp.raw._sock.getpeername()[1]
        ip = ipaddress.IPv4Address(ip_string)
    except requests.exceptions.ConnectTimeout:
        # The request timed out while trying to connect to the remote server.
        # Requests that produced this error are safe to retry.
        raise
    except requests.exceptions.ConnectionError:
        # A Connection error occurred. This occurs if https is not supported by the server
        raise
    except requests.exceptions.HTTPError:
        # An HTTP error occurred.
        raise
    except requests.exceptions.URLRequired:
        # A valid URL is required to make a request.
        raise
    except requests.exceptions.InvalidURL:
        raise
    except requests.exceptions.TooManyRedirects:
        # Too many redirects.
        raise
    except requests.exceptions.ReadTimeout:
        # The server did not send any data in the allotted amount of time.
        raise
    except requests.exceptions.Timeout:
        # The request timed out. Catching this error will catch both ConnectTimeout and ReadTimeout errors.
        raise
    except requests.exceptions.RequestException:
        # There was an ambiguous exception that occurred while handling your request.
        raise
    if response.headers.get('strict-transport-security') is not None:
        hsts = True
    else:
        hsts = False
    redirection_path.append(response.url)  # final page
    landing_url = SchemeUrl(response.url)
    return landing_url, redirection_path, hsts, ip


def download_latest_tsv_database(project_root_directory=Path.cwd()) -> None:
    """
    Download the .tsv database from the site, extract it and finally delete the archive. Everything in the input folder.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
    returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
    return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
    to default as if the entry point is main.py file (which is the only entry point considered).

    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    """
    url = 'https://iptoasn.com/data/ip2asn-v4.tsv.gz'
    r = requests.get(url, allow_redirects=True)
    with open(f"{str(project_root_directory)}{os.sep}{INPUT_FOLDER_NAME}{os.sep}{IP_ASN_ARCHIVE_NAME}", 'wb') as d:
        d.write(r.content)
        d.close()
        extract_gz_archive(project_root_directory=project_root_directory)


def extract_gz_archive(project_root_directory=Path.cwd()) -> None:
    """
    Extract the first .gz archive found in the input folder.
    Then it deletes the archive.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
    returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
    return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
    to default as if the entry point is main.py file (which is the only entry point considered).

    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    """
    file_archive_extracted_name = IP_ASN_ARCHIVE_NAME.replace('.gz', '')
    try:
        result = file_utils.search_for_file_type_in_subdirectory(INPUT_FOLDER_NAME, ".gz", project_root_directory=project_root_directory)
    except FileWithExtensionNotFoundError:
        raise
    archive = result[0]
    file = file_utils.set_file_in_folder(INPUT_FOLDER_NAME, file_archive_extracted_name, project_root_directory=project_root_directory)
    file_content = None
    with gzip.open(f"{str(archive)}", 'rb') as ar:
        file_content = ar.read()        # if content is very large, lots of RAM is occupied
        ar.close()
    with open(f"{str(file)}", 'wb') as f:
        f.write(file_content)
        f.close()
        archive.unlink()
