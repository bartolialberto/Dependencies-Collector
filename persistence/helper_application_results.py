from typing import Dict, Tuple
from entities.LandingResolver import WebSiteLandingResult
from persistence import helper_website, helper_website_lands, helper_webserver
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
