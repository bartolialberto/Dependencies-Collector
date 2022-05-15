import platform


def get_geckodriver_filename() -> str:
    """
    Static method that returns the filename of the geckodriver file to be used in the application based on the
    OS.

    :raise ValueError: If an unexpected value is computed.
    :return: Geckodriver filename.
    :rtype: str
    """
    if platform.system() == 'Linux':
        return 'geckodriver'
    elif platform.system() == 'Windows':
        return 'geckodriver.exe'
    elif platform.system() == 'Darwin':
        return 'geckodriver'
    else:
        raise ValueError


# SQLite file name
SQLite_DATABASE_FILE_NAME = 'results.sqlite'
# command line arguments
ARGUMENT_CONSIDER_TLD = '-tld'
ARGUMENT_COMPLETE_DATABASE = '-continue'
ARGUMENT_RESOLVE_SCRIPT = '-script'
ARGUMENT_SCRAPE_ROV = '-rov'
# project folders
OUTPUT_FOLDER_NAME = 'output'
INPUT_FOLDER_NAME = 'input'
SNAPSHOTS_FOLDER_NAME = 'SNAPSHOTS'
# input file names
INPUT_MAIL_DOMAINS_FILE_NAME = 'mail_domains.txt'
INPUT_WEB_SITES_FILE_NAME = 'web_pages.txt'
IP_ASN_ARCHIVE_NAME = 'ip2asn-v4.tsv.gz'
GECKODRIVER_FILENAME = get_geckodriver_filename()
