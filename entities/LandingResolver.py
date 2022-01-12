from ipaddress import IPv4Address
from typing import Tuple, List, Dict, Set
import requests

from entities.error_log.ErrorLog import ErrorLog
from utils import requests_utils, url_utils


class SiteLandingResult:
    def __init__(self, url: str, redirection_path: List[str], hsts: bool, ip: IPv4Address):
        self.url = url
        self.redirection_path = redirection_path
        self.hsts = hsts
        self.ip = ip
        self.server = url_utils.deduct_second_component(url)


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

    def resolve_web_sites(self, web_sites: Set[str]) -> Tuple[Dict[str, Tuple[SiteLandingResult, SiteLandingResult]], List[ErrorLog]]:
        result = dict()
        error_logs = list()
        for web_site in web_sites:
            print(f"Trying to resolve landing page of web site: {web_site}")
            https_result, http_result, temp_error_logs = self.resolve_web_site(web_site)
            result[web_site] = (https_result, http_result)

            for log in temp_error_logs:
                error_logs.append(log)

            # HTTPS
            print(f"***** via HTTPS *****")
            if result[web_site][0] is not None:
                print(f"HTTPS Landing url: {https_result.url}")
                print(f"HTTPS WebServer: {https_result.server}")
                print(f"HTTPS IP: {https_result.ip.compressed}")
                print(f"Strict Transport Security: {https_result.hsts}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(https_result.redirection_path):
                    print(f"----> [{index + 1}/{len(https_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            if result[web_site][1] is not None:
                print(f"HTTP Landing url: {http_result.url}")
                print(f"HTTP WebServer: {http_result.server}")
                print(f"HTTP IP: {http_result.ip.compressed}")
                print(f"Strict Transport Security: {http_result.hsts}")
                print(f"HTTP Redirection path:")
                for index, url in enumerate(http_result.redirection_path):
                    print(f"----> [{index + 1}/{len(http_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTP...")
            print()
        return result, error_logs

    def resolve_web_site(self, web_site: str) -> Tuple[SiteLandingResult, SiteLandingResult, List[ErrorLog]]:
        error_logs = list()
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(web_site, as_https=True)
            https_result = SiteLandingResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
        except requests.exceptions.ConnectionError as e:
            # probably the server doesn't support HTTPS
            https_result = None
            error_logs.append(ErrorLog(e, web_site, str(e)))
        except Exception as exc:
            https_result = None
            error_logs.append(ErrorLog(exc, web_site, str(exc)))
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(web_site, as_https=False)
            http_result = SiteLandingResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
        except Exception as exc:
            http_result = None
            error_logs.append(ErrorLog(exc, web_site, str(exc)))
        return https_result, http_result, error_logs

    def resolve_script_sites(self, script_sites: Set[str]) -> Tuple[Dict[str, Tuple[SiteLandingResult, SiteLandingResult]], List[ErrorLog]]:
        result = dict()
        error_logs = list()
        for script_site in script_sites:
            print(f"Trying to resolve landing page of script site: {script_site}")
            https_result, http_result, temp_error_logs = self.resolve_script_site(script_site)
            result[script_site] = (https_result, http_result)

            for log in temp_error_logs:
                error_logs.append(log)

            # HTTPS
            print(f"***** via HTTPS *****")
            if result[script_site][0] is not None:
                print(f"HTTPS Landing url: {https_result.url}")
                print(f"HTTPS ScriptServer: {https_result.server}")
                print(f"HTTPS IP: {https_result.ip.compressed}")
                print(f"Strict Transport Security: {https_result.hsts}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(https_result.redirection_path):
                    print(f"----> [{index + 1}/{len(https_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            if result[script_site][1] is not None:
                print(f"HTTP Landing url: {http_result.url}")
                print(f"HTTP ScriptServer: {http_result.server}")
                print(f"HTTP IP: {http_result.ip.compressed}")
                print(f"Strict Transport Security: {http_result.hsts}")
                print(f"HTTP Redirection path:")
                for index, url in enumerate(http_result.redirection_path):
                    print(f"----> [{index + 1}/{len(http_result.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTP...")
            print()
        return result, error_logs

    def resolve_script_site(self, script_site: str) -> Tuple[SiteLandingResult, SiteLandingResult, List[ErrorLog]]:
        error_logs = list()
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(script_site, as_https=True)
            https_result = SiteLandingResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
        except requests.exceptions.ConnectionError as e:
            # probably the server doesn't support HTTPS
            https_result = None
            error_logs.append(ErrorLog(e, script_site, str(e)))
        except Exception as exc:
            https_result = None
            error_logs.append(ErrorLog(exc, script_site, str(exc)))
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(script_site,
                                                                                                 as_https=True)
            http_result = SiteLandingResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
        except Exception as exc:
            http_result = None
            error_logs.append(ErrorLog(exc, script_site, str(exc)))
        return https_result, http_result, error_logs

