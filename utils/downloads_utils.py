import os
from pathlib import Path
import requests
import gzip
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import file_utils


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
