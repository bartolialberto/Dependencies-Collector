import sys
from typing import List, Tuple
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from SNAPSHOTS.take_snapshot import take_snapshot
from pathlib import Path
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from persistence import helper_application_results
from persistence.BaseModel import db
from utils import network_utils, list_utils, file_utils, snapshot_utils


def get_input_websites(default_websites=('google.it/doodles', 'www.youtube.it/feed/explore')) -> List[str]:
    """
    Start of the application: getting the websites, and returning them as a list of string.
    They can be set from command line and from a file name websites.txt put in the input folder in which each website is
    written per line. The application will control first the command line and then the file. If no website is set
    neither in the 2 ways, the application will start with 2 default websites show its behaviour.
    Such websites are: google.it/doodles, www.youtube.it/feed/explore.

    :param default_websites: The default websites to use when no one is set by the user.
    :type default_websites: Tuple[str]
    :return: The list of computed websites.
    :rtype: List[str]
    """
    print(f"******* COMPUTING INPUT WEB SITES *******")
    return get_input_generic_file('web_sites.txt', default_websites)


def get_input_mail_domains(default_mail_domains=('gmail.com', 'outlook.com')) -> List[str]:
    """
    Start of the application: getting the mail domains, and returning them as a list of string.
    They can be set from command line and from a file name mail_domains.txt put in the input folder in which each mail
    domain is written per line. The application will control first the command line and then the file. If no mail domain
    is set neither in the 2 ways, the application will start with 2 default mail domains show its behaviour.
    Such mail domains are: gmail.com, outlook.com.

    :param default_mail_domains: The default mail domains to use when no one is set by the user.
    :type default_mail_domains: Tuple[str]
    :return: The list of computed mail domains.
    :rtype: List[str]
    """
    print(f"******* COMPUTING INPUT MAIL DOMAINS *******")
    return get_input_generic_file('mail_domains.txt', default_mail_domains)


def get_input_generic_file(input_filename: str, default_values: tuple) -> List[str]:
    """
    Auxiliary method that parses input from the filename parameter in the 'input' folder of the application.
    Also it can be set a default collection of values if the file is not not present.

    :param input_filename: The input filename with the extension.
    :type input_filename: str
    :param default_values: The default values.
    :type default_values: tuple
    :return: The list of computed mail values.
    :rtype: List[str]
    """
    result_list = list()
    if len(sys.argv) == 1:
        print(f"> No values found in command line.")
        search_result = None
        try:
            search_result = file_utils.search_for_filename_in_subdirectory('input', input_filename)
        except FilenameNotFoundError:
            print(f"> No '{input_filename}' file found in 'input' folder found.")
            print(f"> Starting application with default values as sample:")
            result_list = list(default_values)
            for index, mail_domain in enumerate(result_list):
                print(f"> [{index + 1}/{len(result_list)}]: {mail_domain}")
            return result_list
        file = search_result[0]
        abs_filepath = str(file)
        with open(abs_filepath, 'r') as f:  # 'w' or 'x'
            print(f"> Found '{input_filename}' file in 'input' folder.")
            lines = f.readlines()
            for i, line in enumerate(lines):
                candidate = line.rstrip()  # strip from whitespaces and EOL (End Of Line)
                print(f"> [{i + 1}/{len(lines)}]: {line}")
                result_list.append(candidate)
            f.close()
            if len(result_list) == 0:
                print(f"> File {input_filename} in 'input' folder doesn't contain any valid input.")
                exit(0)
    else:
        print('> Argument List:', str(sys.argv))
        for arg in sys.argv[1:]:
            result_list.append(arg)
        print(f"> Parsed {len(result_list)} well-formatted inputs:")
        for index, value in enumerate(result_list):
            print(f"> [{index + 1}/{len(result_list)}]: {value}")
    result_list = list_utils.remove_duplicates(result_list)
    return result_list


def get_input_application_flags(persist_errors=False, consider_tld=False) -> Tuple[bool, bool]:
    """
    Start of the application: getting the parameters that can personalized the elaboration of the application.
    Such parameters (properties: they can be set or not set) are:

    1- persist_errors: a flag that set the will to save the explicit lack of results in database between entities (where
    it is possible)

    2- consider_tld: a flag that will consider or remove the Top-Level Domains when computing zone dependencies

    :param persist_errors: The default value of the flag.
    :type persist_errors: bool
    :param consider_tld: The default value of the flag.
    :type consider_tld: bool
    :return: A tuple of booleans for each flag.
    :rtype: Tuple[bool]
    """
    print(f"******* COMPUTING INPUT FLAGS *******")
    print('> Argument List:', str(sys.argv))
    for arg in sys.argv[1:]:
        if arg == 'qualcosa_da_definire':
            persist_errors = True
        if arg == 'qualcosa_da_definire':
            consider_tld = True
    print(f"> PERSIST_ERRORS flag: {str(persist_errors)}")
    print(f"> CONSIDER_TLDs flag: {str(consider_tld)}")
    return persist_errors, consider_tld


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
        print("********** START ACTUAL APPLICATION ELABORATION **********")
        resolvers = ApplicationResolversWrapper(consider_tld)
        headless_browser_is_instantiated = True
        # auxiliary elaborations
        resolvers.dns_resolver.cache.take_temp_snapshot()  # for future error reproducibility
        snapshot_utils.take_temporary_snapshot(input_websites, input_mail_domains, persist_errors, consider_tld)    # for future error reproducibility
        # actual elaboration of all resolvers
        preamble_domain_names = resolvers.do_preamble_execution(input_websites, input_mail_domains)
        midst_domain_names = resolvers.do_midst_execution(preamble_domain_names)
        resolvers.do_epilogue_execution(midst_domain_names)
        # insertion in the database
        print("\nInsertion into database started... ")
        helper_application_results.insert_all_application_results(resolvers, persist_errors)
        print("Insertion into database finished.")
        # export dns cache and error_logs
        resolvers.dns_resolver.cache.write_to_csv_in_output_folder()
        resolvers.error_logger.write_to_csv_in_output_folder()
    except Exception as e:
        take_snapshot(e)
        print(f"!!! Unexpected exception occurred. SNAPSHOT taken. !!!")
        print(f"!!! type: {type(e)} !!!")
        print(f"!!! str: {str(e)} !!!")
    finally:
        # closing
        if headless_browser_is_instantiated:
            resolvers.headless_browser.close()
        db.close()
    print("********** APPLICATION END **********")
