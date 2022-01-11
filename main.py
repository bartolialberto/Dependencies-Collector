import ipaddress
import sys
from typing import List, Tuple
from entities.ApplicationResolvers import ApplicationResolvers
from SNAPSHOTS.take_snapshot import take_snapshot
from pathlib import Path
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from persistence import helper_application_results
from persistence.BaseModel import db
from utils import network_utils, list_utils, file_utils
from utils import domain_name_utils


def get_input_websites(default_websites=('google.it/doodles', 'www.youtube.it/feed/explore')) -> List[str]:
    """
    Start of the application: getting the domain names, and returning them as a list of string.
    They can be set from command line and from a .txt file put in the input folder in which each domain name is written
    per line. The application will control first the command line and then the file. If no domain name is set neither in
    the 2 ways, the application will start with 2 default domain names to show its behaviour.
    Such domain names are: google.it, youtube.it.
    Every domain name is checked if matches the correct rules of defining a domain name. Then, at the end, duplicates
    are removed.

    :param default_websites: The default domain names to use when no one is set by the user.
    :type default_websites: List[str]
    :return: A list of 'grammatically' correct domain names.
    :rtype: List[str]
    """
    websites = list()
    if len(sys.argv) == 1:
        print(f"> No domain names found in command line.")
        result = None
        try:
            result = file_utils.search_for_file_type_in_subdirectory("input", ".txt")
        except FileWithExtensionNotFoundError:
            print(f"> No .txt file found in input folder found.")
            print(f"> Starting application with default websites as sample:")
            websites = list(default_websites)
            for index, website in enumerate(websites):
                print(f"> [{index + 1}/{len(websites)}]: {website}")
            return websites
        file = result[0]
        abs_filepath = str(file)
        with open(abs_filepath, 'r') as f:  # 'w' or 'x'
            print(f"> Found file: {abs_filepath}")
            lines = f.readlines()
            for line in lines:
                candidate = line.rstrip()  # strip from whitespaces and EOL (End Of Line)
                if domain_name_utils.is_grammatically_correct(candidate):
                    websites.append(candidate)
                else:
                    pass
            f.close()
            if len(websites) == 0:
                print(f"> The .txt file in input folder doesn't contain any valid website.")
                exit(0)
    else:
        print('> Argument List:', str(sys.argv))
        for arg in sys.argv[1:]:
            if domain_name_utils.is_grammatically_correct(arg):
                pass
            else:
                print(f"!!! {arg} is not a well-formatted domain name. !!!")
        if len(websites) == 0:
            print(f"!!! Command line arguments are not well-formatted websites. !!!")
            exit(1)
        else:
            print(f"> Parsed {len(websites)} well-formatted domain names:")
            for index, website in enumerate(websites):
                print(f"> [{index + 1}/{len(websites)}]: {website}")
    list_utils.remove_duplicates(websites)
    return websites


def get_input_mail_domains(default_mail_domains=('mail.google.it', 'mail.dei.unipd.it')) -> List[str]:
    """
    Start of the application: getting the domain names, and returning them as a list of string.
    They can be set from command line and from a .txt file put in the input folder in which each domain name is written
    per line. The application will control first the command line and then the file. If no domain name is set neither in
    the 2 ways, the application will start with 2 default domain names to show its behaviour.
    Such domain names are: google.it, youtube.it.
    Every domain name is checked if matches the correct rules of defining a domain name. Then, at the end, duplicates
    are removed.

    :param default_websites: The default domain names to use when no one is set by the user.
    :type default_websites: List[str]
    :return: A list of 'grammatically' correct domain names.
    :rtype: List[str]
    """
    mail_domains = list()
    if len(sys.argv) == 1:
        print(f"> No mail domains found in command line.")
        result = None
        try:
            result = file_utils.search_for_file_type_in_subdirectory("input", ".txt")
        except FileWithExtensionNotFoundError:
            print(f"> No .txt file found in input folder found.")
            print(f"> Starting application with default mail domains as sample:")
            mail_domains = list(default_mail_domains)
            for index, mail_domain in enumerate(mail_domains):
                print(f"> [{index + 1}/{len(mail_domains)}]: {mail_domain}")
            return mail_domains
        file = result[0]
        abs_filepath = str(file)
        with open(abs_filepath, 'r') as f:  # 'w' or 'x'
            print(f"> Found file: {abs_filepath}")
            lines = f.readlines()
            for line in lines:
                candidate = line.rstrip()  # strip from whitespaces and EOL (End Of Line)
                if domain_name_utils.is_grammatically_correct(candidate):
                    mail_domains.append(candidate)
                else:
                    pass
            f.close()
            if len(mail_domains) == 0:
                print(f"> The .txt file in input folder doesn't contain any valid mail domain.")
                exit(0)
    else:
        print('> Argument List:', str(sys.argv))
        for arg in sys.argv[1:]:
            if domain_name_utils.is_grammatically_correct(arg):
                pass
            else:
                print(f"!!! {arg} is not a well-formatted domain name. !!!")
        if len(mail_domains) == 0:
            print(f"!!! Command line arguments are not well-formatted domain names. !!!")
            exit(1)
        else:
            print(f"> Parsed {len(mail_domains)} well-formatted mail domains:")
            for index, mail_domain in enumerate(mail_domains):
                print(f"> [{index + 1}/{len(mail_domains)}]: {mail_domain}")
    list_utils.remove_duplicates(mail_domains)
    return mail_domains


def get_input_application_flags(default_persist_errors=True, default_consider_tld=False) -> Tuple[bool, bool]:
    """
    Start of the application: getting the intention of persist errors in the database.

    :param default_persist_errors: The default value of the flag.
    :type default_persist_errors: bool
    :return: A boolean to set the flag.
    :rtype: bool
    """
    print('> Argument List:', str(sys.argv))
    for arg in sys.argv[1:]:
        if arg == 'qualcosa_da_definire':
            default_persist_errors = True
        if arg == 'qualcosa_da_definire':
            default_consider_tld = True
    return default_persist_errors, default_consider_tld


if __name__ == "__main__":
    print("********** START APPLICATION **********")
    headless_browser_is_instantiated = False
    try:
        print(f"Local IP: {network_utils.get_local_ip()}")
        print(f"Current working directory ( Path.cwd() ): {Path.cwd()}")
        # application input
        input_websites = get_input_websites()
        input_mail_domains = get_input_mail_domains()
        persist_errors, consider_tld = get_input_application_flags()
        # entities
        resolvers = ApplicationResolvers(consider_tld)
        headless_browser_is_instantiated = True
        # auxiliary elaborations
        domain_name_utils.take_snapshot(input_websites)   # for future error reproducibility
        resolvers.dns_resolver.cache.take_snapshot()        # for future error reproducibility
        # actual elaboration of all resolvers
        preamble_domain_names = resolvers.do_preamble_execution(input_websites, input_mail_domains)
        midst_domain_names = resolvers.do_midst_execution(preamble_domain_names)
        resolvers.do_epilogue_execution(midst_domain_names)
        # insertion in the database
        print("Insertion into database... ", end='')
        helper_application_results.insert_landing_websites_results(resolvers.landing_web_sites_results)
        helper_application_results.insert_mail_servers_resolving(resolvers.mail_servers_results)
        helper_application_results.insert_dns_result(resolvers.total_dns_results,
                                                     resolvers.total_zone_dependencies_per_zone,
                                                     resolvers.total_zone_dependencies_per_name_server)
        # helper_domain_name.multiple_inserts(resolvers.dns_results)
        # helper_landing_page.multiple_inserts(resolvers.landing_page_results)
        # helper_content_dependency.multiple_inserts(resolvers.content_dependencies_results)
        # helper_matches.insert_all_entries_associated(results)
        print("DONE.")
        # export dns cache and error_logs
        resolvers.dns_resolver.cache.write_to_csv_in_output_folder()
        resolvers.error_logger.write_to_csv_in_output_folder()
    except Exception as e:
        take_snapshot(e)
        print(f"!!! Unexpected exception occurred. SNAPSHOT taken. !!!")
        print(f"!!! {str(e)} !!!")
    finally:
        # closing
        if headless_browser_is_instantiated:
            resolvers.headless_browser.close()
        db.close()
    print("********** APPLICATION END **********")
