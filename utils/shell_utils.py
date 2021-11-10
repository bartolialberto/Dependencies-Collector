from pathlib import Path
from typing import List
from exceptions.FileWithExtensionNotFoundError import FileWithExtensionNotFoundError
from exceptions.NoValidDomainNamesFoundError import NoValidDomainNamesFoundError
from utils import domain_name_utils, file_utils
from utils.file_utils import search_for_file_type_in_subdirectory


def wait_yes_or_no_response(response_legend: str) -> str:
    done = False
    while not done:
        answer = input(response_legend)
        if answer == 'y' or answer == 'Y':
            return 'y'
        elif answer == 'n' or answer == 'N':
            return 'n'
        else:
            pass


def wait_how_to_load_domain_names_response() -> int:
    print(f"> No command line arguments found. Do you want to load them from file or write it down now?")
    print(f"> Press 0 for load a .txt file situated in the 'input' folder (application will take the first .txt file found)")
    print(f"> Press 1 for write down each ofthem here")
    done = False
    while not done:
        answer = input("> ")
        try:
            answer_int = int(answer)
        except ValueError:
            print("> Not an expected response.")
            continue
        if answer_int == 0:
            return 0
        elif answer_int == 1:
            return 1
        else:
            print("> Not an expected response.")


def wait_domain_names_typing() -> List[str]:
    domain_name_list = list()
    done = False
    while not done:
        print(f"> Current domain name list: {str(domain_name_list)}")
        print(f"> Write 'ok' to finish")
        print(f"> Write 'del' to delete last element of the list.")
        print(f"> Write a domain name and then enter to add.")
        answer = input(f"> ")
        if answer == 'ok' or answer == 'OK':
            if len(domain_name_list) == 0:
                print(f"> You haven't typed a single domain name...")
            else:
                done = True
                return domain_name_list
        elif answer == 'del' or answer == 'DEL':
            try:
                domain_name_list.pop()
            except IndexError:
                print(f"!!! you can't delete from an empty list !!!")
        else:
            if domain_name_utils.is_grammatically_correct(answer):
                domain_name_list.append(answer)
            else:
                print(f"!!! {answer} is not a well-formatted domain name. !!!")


def handle_getting_domain_names_from_txt_file() -> List[str]:
    try:
        result = search_for_file_type_in_subdirectory(Path.cwd(), "input", ".txt")
    except FileWithExtensionNotFoundError:
        raise
    file = result[0]
    domain_list = list()
    abs_filepath = str(file)
    with open(abs_filepath, 'r') as f:       # 'w' or 'x'
        print(f"> Found file: {abs_filepath}")
        lines = f.readlines()
        for line in lines:
            candidate = line.rstrip()       # strip from whitespaces and EOL (End Of Line)
            if domain_name_utils.is_grammatically_correct(candidate):
                domain_list.append(candidate)
            else:
                pass
        f.close()
        if len(domain_list) == 0:
            raise NoValidDomainNamesFoundError(abs_filepath)
        else:
            return domain_list


def wait_enter_to_confirm(title="Press enter to confirm.."):
    print(title)
    done = False
    while not done:
        answer = input("> ")
        if answer == "":
            done = True
        else:
            pass
