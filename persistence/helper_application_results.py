from typing import Dict, Tuple, List

from peewee import DoesNotExist

from entities.LandingResolver import WebSiteLandingResult
from entities.Zone import Zone
from entities.error_log.ErrorLog import ErrorLog
from persistence import helper_website, helper_website_lands, helper_webserver, helper_zone, helper_nameserver, \
    helper_zone_links, helper_name_dependencies, helper_domain_name
from utils import url_utils


def insert_landing_page_result(result: Dict[str, Tuple[WebSiteLandingResult, WebSiteLandingResult]], persist_errors=True):
    for website in result.keys():
        wse = helper_website.insert(website)
        helper_website_lands.delete_all_from_website_entity(wse)

        # HTTPS result
        is_https = True
        if result[website][0] is None and persist_errors == True:
            helper_website_lands.insert(wse, None, is_https)
        elif result[website][0] is None and persist_errors == False:
            pass
        else:
            webserver_https = url_utils.deduct_http_url(result[website][0].url, as_https=is_https)
            wsvr_https = helper_webserver.insert(webserver_https)
            helper_website_lands.insert(wse, wsvr_https, is_https)

        # HTTP result
        is_https = False
        if result[website][1] is None and persist_errors == True:
            helper_website_lands.insert(wse, None, is_https)
        elif result[website][1] is None and persist_errors == False:
            pass
        else:
            webserver_http = url_utils.deduct_http_url(result[website][1].url, as_https=is_https)
            wsvr_http = helper_webserver.insert(webserver_http)
            helper_website_lands.insert(wse, wsvr_http, is_https)


def insert_dns_result(result: tuple, persist_errors=True):
    zone_dependencies_per_domain_name = result[0]
    zone_dependencies_per_zone = result[1]
    zone_names_per_nameserver = result[2]
    error_logs = result[3]

    ze_dict = dict()
    nse_dict = dict()

    for domain_name in zone_dependencies_per_domain_name.keys():
        dne = helper_domain_name.insert(domain_name)
        for zone in zone_dependencies_per_domain_name[domain_name]:
            ze = helper_zone.insert_zone_object(zone)
            helper_name_dependencies.insert(dne, ze)

            ze_dict[zone.name] = ze

    for zone_name in zone_dependencies_per_zone.keys():
        """
        try:
            ze = helper_zone.get(zone_name)
        except DoesNotExist:
            raise
        """

        try:
            ze = ze_dict[zone_name]
        except KeyError:
            raise

        for zone_dependency in zone_dependencies_per_zone[zone_name]:
            # ze_dep = helper_zone.get(zone_dependency)

            try:
                ze_dep = ze_dict[zone_dependency]
            except KeyError:
                raise

            helper_zone_links.insert(ze, ze_dep)

    for nameserver in zone_names_per_nameserver.keys():
        try:
            nse, dne = helper_nameserver.get(nameserver)
        except DoesNotExist:
            raise
        for zone_name in zone_names_per_nameserver[nameserver]:
            """
            try:
                ze = helper_zone.get(zone_name)
            except DoesNotExist:
                raise
            """

            try:
                ze = ze_dict[zone_name]
            except DoesNotExist:
                raise

            helper_name_dependencies.insert(dne, ze)
