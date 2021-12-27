from ipaddress import IPv4Address
from typing import Tuple, List, Dict
import requests
from utils import domain_name_utils, requests_utils


class WebSiteLandingResult:
    def __init__(self, url: str, redirection_path: List[str], hsts: bool, ip: IPv4Address):
        self.url = url
        self.redirection_path = redirection_path
        self.hsts = hsts
        self.ip = ip


class LandingResolver:
    '''
    except requests.exceptions.ConnectionError as e:
        pass
    except requests.exceptions.ConnectTimeout as e:
        pass
    except requests.exceptions.URLRequired as e:
        pass
    except requests.exceptions.TooManyRedirects as e:
        pass
    except requests.exceptions.ReadTimeout as e:
        pass
    except requests.exceptions.Timeout as e:
        pass
    except requests.exceptions.RequestException as e:
        pass
    '''

    def __init__(self):
        pass

    def resolve_landing_pages(self, websites: List[str]) -> Dict[str, Tuple[WebSiteLandingResult, WebSiteLandingResult]]:
        result = dict()
        for website in websites:
            try:
                print(f"Trying to resolve landing page of '{website}':")
                result[website] = self.resolve_landing_page(website)

                # HTTPS
                print(f"***** via HTTPS *****")
                if result[website][0] is not None:
                    https_result = result[website][0]
                    print(f"HTTPS Landing url: {https_result.url}")
                    print(f"HTTPS IP: {https_result.ip.compressed}")
                    print(f"Strict Transport Security: {https_result.hsts}")
                    print(f"HTTPS Redirection path:")
                    for index, url in enumerate(https_result.redirection_path):
                        print(f"----> [{index + 1}/{len(https_result.redirection_path)}]: {url}")
                else:
                    print(f"Impossible to land somewhere via HTTPS...")

                # HTTP
                print(f"***** via HTTP *****")
                if result[website][1] is not None:
                    http_result = result[website][1]
                    print(f"HTTP Landing url: {http_result.url}")
                    print(f"HTTP IP: {http_result.ip.compressed}")
                    print(f"Strict Transport Security: {http_result.hsts}")
                    print(f"HTTP Redirection path:")
                    for index, url in enumerate(http_result.redirection_path):
                        print(f"----> [{index + 1}/{len(http_result.redirection_path)}]: {url}")
                else:
                    print(f"Impossible to land somewhere via HTTP...")

                print()
            except Exception:
                raise
        return result

    def resolve_landing_page(self, website: str) -> Tuple[WebSiteLandingResult, WebSiteLandingResult]:
        try:
            temp = requests_utils.resolve_landing_page(website, as_https=True)
            https_result = WebSiteLandingResult(temp[0], temp[1], temp[2], IPv4Address(temp[3]))
        except requests.exceptions.ConnectionError as e:
            # probably the server doesn't support HTTPS
            https_result = None
        except Exception:
            raise
        try:
            temp = requests_utils.resolve_landing_page(website, as_https=False)
            http_result = WebSiteLandingResult(temp[0], temp[1], temp[2], IPv4Address(temp[3]))
        except Exception:
            raise
        return https_result, http_result

    def resolve_script_site(self, script_url: str):
        script_site = domain_name_utils.deduct_domain_name(script_url)
        try:
            https_result = requests_utils.resolve_landing_page(script_site)
        except requests.exceptions.ConnectionError as e:
            # probably the server doesn't support HTTPS
            https_result = None
        except Exception:
            https_result = None
        try:
            http_result = requests_utils.resolve_landing_page(script_site, as_https=False)
        except Exception:
            http_result = None

