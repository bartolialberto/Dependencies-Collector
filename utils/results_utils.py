from utils import domain_name_utils


def merge_dns_results(total_dns_result: dict, new_dns_result: dict):
    for domain_name in new_dns_result.keys():
        try:
            total_dns_result[domain_name]
        except KeyError:
            total_dns_result[domain_name] = new_dns_result[domain_name]


def merge_ip_as_db_results(total_ip_as_db_results: dict, new_ip_as_db_results: dict):
    for nameserver in new_ip_as_db_results.keys():
        try:
            total_ip_as_db_results[nameserver]
        except KeyError:
            total_ip_as_db_results[nameserver] = new_ip_as_db_results[nameserver]


def merge_landing_page_results(total_landing_page_results: dict, new_loading_page_results: dict):
    for domain_name in new_loading_page_results.keys():
        try:
            total_landing_page_results[domain_name]
        except KeyError:
            total_landing_page_results[domain_name] = new_loading_page_results[domain_name]


def merge_content_dependencies_results(total_content_dependencies__results: dict, new_content_dependencies_results: dict):
    for landing_page in new_content_dependencies_results.keys():
        try:
            total_content_dependencies__results[landing_page]
        except KeyError:
            total_content_dependencies__results[landing_page] = new_content_dependencies_results[landing_page]
