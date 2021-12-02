import sys
from typing import List
from entities.ApplicationResolvers import ApplicationResolvers
from persistence import helper_domain_name, helper_landing_page, helper_content_dependency, helper_matches
from persistence.BaseModel import db
from SNAPSHOTS.take_snapshot import take_snapshot
from pathlib import Path
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from utils import network_utils, list_utils, file_utils
from utils import domain_name_utils


def get_domain_names() -> List[str]:
    """
    Start of the application: getting the domain names, and returning them as a list of string.
    They can be set from command line and from a .txt file put in the input folder in which each domain name is written
    per line. The application will control first the command line and then the file. If no domain name is set neither in
    the 2 ways, the application will start with 2 default domain names to show its behaviour.
    Such domain names are: google.it, youtube.it.
    Every domain name is checked if matches the correct rules of defining a domain name. Then, at the end, duplicates
    are removed.

    :return: A list of 'grammatically' correct domain names.
    :rtype: List[str]
    """
    domain_name_list = list()
    if len(sys.argv) == 1:
        print(f"> No domain names found in command line.")
        result = None
        try:
            result = file_utils.search_for_file_type_in_subdirectory("input", ".txt")
        except FileWithExtensionNotFoundError:
            print(f"> No .txt file found in input folder found.")
            print(f"> Starting application with default domain names as sample:")
            domain_name_list.append('google.it')       # darklyrics.com works only on HTTP
            domain_name_list.append('youtube.it')
            for index, domain_name in enumerate(domain_name_list):
                print(f"> [{index + 1}/{len(domain_name_list)}]: {domain_name}")
            return domain_name_list
        file = result[0]
        abs_filepath = str(file)
        with open(abs_filepath, 'r') as f:  # 'w' or 'x'
            print(f"> Found file: {abs_filepath}")
            lines = f.readlines()
            for line in lines:
                candidate = line.rstrip()  # strip from whitespaces and EOL (End Of Line)
                if domain_name_utils.is_grammatically_correct(candidate):
                    domain_name_list.append(candidate)
                else:
                    pass
            f.close()
            if len(domain_name_list) == 0:
                print(f"> The .txt file in input folder doesn't contain any valid domain name.")
                exit(0)
    else:
        print('> Argument List:', str(sys.argv))
        for arg in sys.argv[1:]:
            if domain_name_utils.is_grammatically_correct(arg):
                pass
            else:
                print(f"!!! {arg} is not a well-formatted domain name. !!!")
        if len(domain_name_list) == 0:
            print(f"!!! Command line arguments are not well-formatted domain names. !!!")
            exit(1)
        else:
            print(f"> Parsed {len(domain_name_list)} well-formatted domain names:")
            for index, domain_name in enumerate(domain_name_list):
                print(f"> [{index + 1}/{len(domain_name_list)}]: {domain_name}")
    list_utils.remove_duplicates(domain_name_list)
    return domain_name_list


if __name__ == "__main__":
    print("********** START APPLICATION **********")
    try:
        print(f"Local IP: {network_utils.get_local_ip()}")
        print(f"Current working directory ( Path.cwd() ): {Path.cwd()}")
        # application input
        new_domain_names = get_domain_names()
        domain_name_utils.take_snapshot(new_domain_names)   # for error future reproducibility
        # entities
        resolvers = ApplicationResolvers()
        resolvers.dns_resolver.cache.take_snapshot()        # for error future reproducibility
        # actual elaboration of all resolvers
        resolvers.do_recursive_cycle_execution(new_domain_names)
        # rov scraping is done outside the recursive cycle
        results = resolvers.do_rov_page_scraping()
        # insertion in the database
        print("Insertion into database... ", end='')
        helper_domain_name.multiple_inserts(resolvers.dns_results)
        helper_landing_page.multiple_inserts(resolvers.landing_page_results)
        helper_content_dependency.multiple_inserts(resolvers.content_dependencies_results)  # FIXME: controllare sul database gli inserimenti
        helper_matches.insert_all_entries_associated(results)       # FIXME: controllare sul database gli inserimenti
        print("DONE.")
        # export cache and error_logs
        resolvers.dns_resolver.cache.write_to_csv_in_output_folder()
        resolvers.error_logger.write_to_csv_in_output_folder('error_logs')
        # closing
        resolvers.headless_browser.close()
        db.close()
    except Exception as e:
        # if happens, kill firefox process in background
        take_snapshot(e)
        print(f"!!! Unexpected exception occurred. SNAPSHOT taken. !!!")
        print(f"!!! {str(e)} !!!")
    print("********** APPLICATION END **********")
