import sys
from datetime import datetime
from typing import List, Tuple
from peewee import SqliteDatabase
from entities.DatabaseEntitiesCompleter import DatabaseEntitiesCompleter
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from SNAPSHOTS.take_snapshot import take_snapshot
from pathlib import Path
from entities.DomainName import DomainName
from entities.Url import Url
from exceptions.FilenameNotFoundError import FilenameNotFoundError
from exceptions.InvalidUrlError import InvalidUrlError
from persistence import helper_application_results, alias_fix
from persistence.BaseModel import db, close_database_connection, db_file
from static_variables import INPUT_FOLDER_NAME, INPUT_MAIL_DOMAINS_FILE_NAME, INPUT_WEB_SITES_FILE_NAME, \
    ARGUMENT_COMPLETE_DATABASE, ARGUMENT_CONSIDER_TLD, ARGUMENT_SCRAPE_ROV, ARGUMENT_RESOLVE_SCRIPT
from utils import network_utils, list_utils, file_utils, snapshot_utils, datetime_utils, database_driver_utils


def get_input_websites(default_websites=('google.it/doodles', 'www.youtube.it/feed/explore'), project_root_directory=Path.cwd()) -> List[Url]:
    """
    Start of the application: getting the websites, and returning them as a list of Url.
    They can be set from a file name web_pages.txt put in the input folder in which each website is
    written per line. If no website is set the application will start with 2 default websites to show its behaviour.
    Such websites are: google.it/doodles, www.youtube.it/feed/explore.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we start the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
    returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
    return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
    to default as if the entry point is main.py file (which is the only entry point considered).

    :param default_websites: The default websites to use when no one is set by the user.
    :type default_websites: Tuple[str]
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    :return: The list of computed websites.
    :rtype: List[Url]
    """
    print(f"******* COMPUTING INPUT WEB SITES *******")
    lines = get_input_generic_file(INPUT_WEB_SITES_FILE_NAME, default_websites, project_root_directory=project_root_directory)
    values = set()
    for line in lines:
        try:
            values.add(Url(line))
        except InvalidUrlError:
            pass
    for i, value in enumerate(values):
        print(f"> [{i+1}/{len(lines)}]: {value}")
    return list(values)


def get_input_mail_domains(default_mail_domains=('gmail.com', 'outlook.com'), project_root_directory=Path.cwd()) -> List[DomainName]:
    """
    Start of the application: getting the mail domains, and returning them as a list of DomainName.
    They can be set from a file name mail_domains.txt put in the input folder in which each mail domain is written per
    line. If no mail domain is set the application will start with 2 default mail domains to show its behaviour.
    Such mail domains are: gmail.com, outlook.com.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we start the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
    returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
    return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
    to default as if the entry point is main.py file (which is the only entry point considered).

    :param default_mail_domains: The default mail domains to use when no one is set by the user.
    :type default_mail_domains: Tuple[str]
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    :return: The list of computed mail domains.
    :rtype: List[DomainName]
    """
    print(f"******* COMPUTING INPUT MAIL DOMAINS *******")
    lines = get_input_generic_file(INPUT_MAIL_DOMAINS_FILE_NAME, default_mail_domains, project_root_directory=project_root_directory)
    values = set()
    for line in lines:
        values.add(DomainName(line))
    for i, value in enumerate(lines):
        print(f"> [{i+1}/{len(lines)}]: {value}")
    return list(values)


def get_input_generic_file(input_filename: str, default_values: tuple, project_root_directory=Path.cwd()) -> List[str]:
    """
    Auxiliary method that parses input from the filename parameter in the 'input' folder of the application.
    Also it can be set a default collection of values if the file is not not present.
    Path.cwd() returns the current working directory which depends upon the entry point of the application; in
    particular, if we start the application from the main.py file in the PRD, every time Path.cwd() is encountered
    (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is
    returned. If the application is started from a file that belongs to the entities package, then Path.cwd() will
    return the entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set
    to default as if the entry point is main.py file (which is the only entry point considered).

    :param input_filename: The input filename with the extension.
    :type input_filename: str
    :param default_values: The default values.
    :type default_values: tuple
    :param project_root_directory: The Path object pointing at the project root directory.
    :type project_root_directory: Path
    :return: The list of strings read.
    :rtype: List[str]
    """
    result_list = list()
    try:
        search_result = file_utils.search_for_filename_in_subdirectory(INPUT_FOLDER_NAME, input_filename, project_root_directory)
    except FilenameNotFoundError:
        print(f"> No '{input_filename}' file found in '{INPUT_FOLDER_NAME}' folder found.")
        print(f"> Starting application with default values as sample:")
        result_list = list(default_values)
        return result_list
    file = search_result[0]
    abs_filepath = str(file)
    with open(abs_filepath, 'r') as f:  # 'w' or 'x'
        print(f"> Found '{input_filename}' file in '{INPUT_FOLDER_NAME}' folder.")
        lines = f.readlines()
        for i, line in enumerate(lines):
            value = line.strip()
            result_list.append(value)
        f.close()
        if len(result_list) == 0:
            print(f"> File {input_filename} in '{INPUT_FOLDER_NAME}' folder doesn't contain any valid input.")
    result_list = list_utils.remove_duplicates(result_list)
    return result_list


def get_input_application_flags(default_complete_unresolved_database=False, default_consider_tld=False, default_execute_script_resolving=False, default_execute_rov_scraping=False) -> Tuple[bool, bool, bool, bool]:
    """
    Start of the application: getting the parameters that can personalized the elaboration of the application.
    Such parameters (properties: they can be set or not set) are:

    1- default_complete_unresolved_database: a flag that sets if the application should try to complete unresolved
    entities (first step of the execution).

    2- default_consider_tld: a flag that sets if Top-Level Domains should be considered when computing zone
    dependencies.

    3- default_execute_script_resolving: a flag that sets if script dependencies resolving should be executed.

    4- default_execute_rov_scraping: a flag that sets if ROVPage scraping should be executed.

    :param default_complete_unresolved_database: The default value of the flag.
    :type default_complete_unresolved_database: bool
    :param default_consider_tld: The default value of the flag.
    :type default_consider_tld: bool
    :param default_execute_script_resolving: The default value of the flag.
    :type default_execute_script_resolving: bool
    :param default_execute_rov_scraping: The default value of the flag.
    :type default_execute_rov_scraping: bool
    :return: A tuple of booleans for each flag.
    :rtype: Tuple[bool, bool, bool ,bool]
    """
    print(f"******* COMPUTING INPUT FLAGS *******")
    print('> Argument List:', str(sys.argv))
    for arg in sys.argv[1:]:
        if arg == ARGUMENT_COMPLETE_DATABASE:
            default_complete_unresolved_database = True
        elif arg == ARGUMENT_CONSIDER_TLD:
            default_consider_tld = True
        elif arg == ARGUMENT_SCRAPE_ROV:
            default_execute_rov_scraping = True
        elif arg == ARGUMENT_RESOLVE_SCRIPT:
            default_execute_script_resolving = True
    print(f"> COMPLETE_UNRESOLVED_DATABASE flag: {str(default_complete_unresolved_database)}")
    print(f"> CONSIDER_TLDs flag: {str(default_consider_tld)}")
    print(f"> EXECUTE SCRIPT RESOLVING flag: {str(default_execute_script_resolving)}")
    print(f"> EXECUTE ROV SCRAPING flag: {str(default_execute_rov_scraping)}")
    return default_complete_unresolved_database, default_consider_tld, default_execute_script_resolving, default_execute_rov_scraping


if __name__ == "__main__":
    print("********** START APPLICATION **********")
    resolvers = None
    try:
        print(f"Local IP: {network_utils.get_local_ip()}")
        print(f"Current working directory ( Path.cwd() ): {Path.cwd()}")
        if isinstance(db, SqliteDatabase):
            print(f"DBMS: SQLite")
            print(f"SQLite driver/module version: {database_driver_utils.get_sqlite_jdbc_version_as_string()}. Is it at least version 3.32.0? {database_driver_utils.check_jdbc_driver_version()}")
            print(f"SQLite runtime library version: {database_driver_utils.get_sqlite_runtime_sqlite_version_as_string()}")
        else:
            print(f"Unhandled database connection..")
        # application input
        input_websites = get_input_websites()
        input_mail_domains = get_input_mail_domains()
        complete_unresolved_database, consider_tld, execute_script_resolving, execute_rov_resolving = get_input_application_flags()
        # entities
        print("********** START APPLICATION **********")
        resolvers = ApplicationResolversWrapper(consider_tld, execute_script_resolving, execute_rov_resolving)
        are_there_new_domain_name_from_db_completion = False
        new_domain_names_from_db_completion = set()
        if complete_unresolved_database:
            completer = DatabaseEntitiesCompleter(resolvers)
            unresolved_entities = helper_application_results.get_unresolved_entities(execute_script_resolving, execute_rov_resolving)
            new_domain_names_from_db_completion = completer.do_complete_unresolved_entities(unresolved_entities)
            if len(new_domain_names_from_db_completion) > 0:
                print(f"From DB completion {len(new_domain_names_from_db_completion)} new domain names will be elaborated from MIDST part onwards.")
                are_there_new_domain_name_from_db_completion = True
        # auxiliary elaborations
        print("********** START ACTUAL APPLICATION ELABORATION **********")
        resolvers.dns_resolver.cache.take_temp_snapshot()  # for future error reproducibility
        snapshot_utils.take_temporary_snapshot(input_websites, input_mail_domains, complete_unresolved_database, consider_tld, execute_script_resolving, execute_rov_resolving)    # for future error reproducibility
        # actual elaboration of all resolvers
        start_execution_time = datetime.now()
        preamble_domain_names = resolvers.do_preamble_execution(input_websites, input_mail_domains)
        if are_there_new_domain_name_from_db_completion:
            list_utils.merge_set_in_list(preamble_domain_names, new_domain_names_from_db_completion)
        midst_domain_names = resolvers.do_midst_execution(preamble_domain_names)
        resolvers.do_epilogue_execution(midst_domain_names)
        # insertion in the database
        print("\nInsertion into database started... ")
        helper_application_results.insert_all_application_results(resolvers)
        df = alias_fix.construct_alias_chained(str(db_file))                # ALIAS CHAINED simplification
        alias_fix.insert_table_in_db(df, str(db_file), 'alias_chained')     # ALIAS CHAINED simplification
        print("Insertion into database finished.")
        # export dns cache, error_logs and unresolved entities
        resolvers.dns_resolver.cache.write_to_csv_in_output_folder()
        resolvers.error_logger.write_to_csv_in_output_folder()
        helper_application_results.dump_all_unresolved_entities(execute_rov_scraping=execute_rov_resolving)
        print(f"Total application execution time is: {datetime_utils.compute_delta_and_stamp(start_execution_time)}")
    except Exception as e:
        take_snapshot(e)
        print(f"!!! Unexpected exception occurred. SNAPSHOT taken. !!!")
        print(f"!!! type: {type(e)} !!!")
        print(f"!!! str: {str(e)} !!!")
    finally:
        # closing
        if resolvers is not None:
            if resolvers.headless_browser_is_instantiated:
                resolvers.headless_browser.close()
        close_database_connection()
    print("********** APPLICATION END **********")
