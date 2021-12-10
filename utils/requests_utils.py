from typing import Tuple, List
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from utils import domain_name_utils
import os
from pathlib import Path
import requests
import gzip
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import file_utils


def resolve_landing_page(domain_name: str, as_https=True) -> Tuple[str, List[str], bool]:
    """
    This method returns the landing page, the redirection path and the HTTP Strict Transport Security validity from a
    domain name. In particular it creates an url from the domain name and then tries a GET HTTP method with it.

    :param domain_name: A domain name.
    :type domain_name: str
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
    :rtype: Tuple[str, List[str], bool]
    """
    redirection_path = list()
    try:
        domain_name_utils.grammatically_correct(domain_name)
    except InvalidDomainNameError:
        raise
    hsts = False
    try:
        url = domain_name_utils.deduct_http_url(domain_name, as_https)
        print(f"URL deducted: {domain_name} ---> {url}")
        response = requests.get(url, headers={'Connection': 'close'})       # FIXME: giusto chiudere subito?
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
    landing_url = response.url
    return landing_url, redirection_path, hsts


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
    with open(f"{str(project_root_directory)}{os.sep}input{os.sep}ip2asn-v4.tsv.gz", 'wb') as d:
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
    try:
        result = file_utils.search_for_file_type_in_subdirectory("input", ".gz", project_root_directory=project_root_directory)
    except FileWithExtensionNotFoundError:
        raise
    archive = result[0]
    file = file_utils.set_file_in_folder("input", "ip2asn-v4.tsv", project_root_directory=project_root_directory)
    file_content = None
    with gzip.open(f"{str(archive)}", 'rb') as ar:
        file_content = ar.read()        # if content is very large, lots of RAM is occupied
        ar.close()
    with open(f"{str(file)}", 'wb') as f:
        f.write(file_content)
        f.close()
        archive.unlink()
