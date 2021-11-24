from typing import Tuple, List
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from utils import domain_name_utils
import os
from pathlib import Path
import requests
import gzip
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import file_utils


def resolve_landing_page(domain_name: str) -> Tuple[str, List[str], bool]:
    """
    This method returns the landing page, the redirecction path and the HTTP Strict Transport Security validity from a
    domain name. In particular it creates an url from the domain name and then tries a GET HTTP method with it.

    :param domain_name: A domain name.
    :type domain_name: str
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
        url = domain_name_utils.deduct_http_url(domain_name, as_https=True)
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
    bool_list = list()
    for resp in response.history:
        redirection_path.append(resp.url)
        if resp.headers.get('strict-transport-security') is not None:
            bool_list.append(True)
        else:
            bool_list.append(False)
    for index, flag in enumerate(bool_list):
        if flag:
            if index == len(bool_list) - 1:
                hsts = True
            else:
                pass
        else:
            hsts = False
            break
    redirection_path.append(response.url)  # final page
    landing_url = response.url
    landing_domain = domain_name_utils.deduct_domain_name(response.url)
    return landing_url, redirection_path, hsts


def download_latest_tsv_database():
    url = 'https://iptoasn.com/data/ip2asn-v4.tsv.gz'
    r = requests.get(url, allow_redirects=True)
    with open(f"{str(Path.cwd())}{os.sep}input{os.sep}ip2asn-v4.tsv.gz", 'wb') as d:
        d.write(r.content)
        d.close()
        extract_gz_archive()


def extract_gz_archive():
    try:
        result = file_utils.search_for_file_type_in_subdirectory("input", ".gz")
    except FileWithExtensionNotFoundError:
        raise
    archive = result[0]
    file = file_utils.set_file_in_folder("input", "ip2asn-v4.tsv")
    file_content = None
    with gzip.open(f"{str(archive)}", 'rb') as ar:
        file_content = ar.read()        # if content is very large, lots of RAM is occupied
        ar.close()
    with open(f"{str(file)}", 'wb') as f:
        f.write(file_content)
        f.close()
        archive.unlink()
