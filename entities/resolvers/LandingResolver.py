from ipaddress import IPv4Address
from typing import Dict, Set
import requests
from entities.error_log.ErrorLog import ErrorLog
from entities.resolvers.results.LandingSiteResult import LandingSiteResult, InnerLandingSiteSingleSchemeResult
from utils import requests_utils


class LandingResolver:
    """
    This class' concern is to provide tools to resolve URL landing.

    """

    def __init__(self):
        """
        Instantiate the object.

        """
        pass

    def resolve_web_sites(self, web_sites: Set[str]) -> Dict[str, LandingSiteResult]:
        """
        This methods resolves landing of all web sites parameters.

        :param web_sites: A set of web sites.
        :type web_sites: Set[str]
        :return: A dictionary with web sites as keys and for each of them the corresponding result.
        :rtype: Dict[str, LandingSiteResult]
        """
        final_results = dict()
        for web_site in web_sites:
            print(f"Trying to resolve landing page of web site: {web_site}")
            resolver_result = self.resolve_web_site(web_site)
            final_results[web_site] = resolver_result

            # HTTPS
            print(f"***** via HTTPS *****")
            if resolver_result.https is not None:
                print(f"HTTPS Landing url: {resolver_result.https.url}")
                print(f"HTTPS WebServer: {resolver_result.https.server}")
                print(f"HTTPS IP: {resolver_result.https.ip.compressed}")
                print(f"Strict Transport Security: {resolver_result.https.hsts}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(resolver_result.https.redirection_path):
                    print(f"----> [{index + 1}/{len(resolver_result.https.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            if resolver_result.http is not None:
                print(f"HTTP Landing url: {resolver_result.http.url}")
                print(f"HTTP WebServer: {resolver_result.http.server}")
                print(f"HTTP IP: {resolver_result.http.ip.compressed}")
                print(f"Strict Transport Security: {resolver_result.http.hsts}")
                print(f"HTTP Redirection path:")
                for index, url in enumerate(resolver_result.http.redirection_path):
                    print(f"----> [{index + 1}/{len(resolver_result.http.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTP...")
            print()
        return final_results

    def resolve_web_site(self, web_site: str) -> LandingSiteResult:
        """
        This methods resolves landing of a web site.
        If an error occurs, it will be added in the error_logs attribute of the result, so exceptions are silent.

        :param web_site: A web site.
        :type web_site: str
        :return: A LandingSiteResult object.
        :rtype: LandingSiteResult
        """
        error_logs = list()
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(web_site, as_https=True)
            https_result = InnerLandingSiteSingleSchemeResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
        except requests.exceptions.ConnectionError as e:
            # probably the server doesn't support HTTPS
            https_result = None
            error_logs.append(ErrorLog(e, web_site, str(e)))
        except Exception as exc:
            https_result = None
            error_logs.append(ErrorLog(exc, web_site, str(exc)))
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(web_site, as_https=False)
            http_result = InnerLandingSiteSingleSchemeResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
        except Exception as exc:
            http_result = None
            error_logs.append(ErrorLog(exc, web_site, str(exc)))
        return LandingSiteResult(https_result, http_result, error_logs)

    def resolve_script_sites(self, script_sites: Set[str]) -> Dict[str, LandingSiteResult]:
        """
        This methods resolves landing of all script sites parameters.

        :param script_sites: A set of web sites.
        :type script_sites: Set[str]
        :return: A dictionary with script sites as keys and for each of them the corresponding result.
        :rtype: Dict[str, LandingSiteResult]
        """
        final_results = dict()
        for script_site in script_sites:
            print(f"Trying to resolve landing page of script site: {script_site}")
            resolver_result = self.resolve_script_site(script_site)
            final_results[script_site] = resolver_result

            # HTTPS
            print(f"***** via HTTPS *****")
            if resolver_result.https is not None:
                print(f"HTTPS Landing url: {resolver_result.https.url}")
                print(f"HTTPS ScriptServer: {resolver_result.https.server}")
                print(f"HTTPS IP: {resolver_result.https.ip.compressed}")
                print(f"Strict Transport Security: {resolver_result.https.hsts}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(resolver_result.https.redirection_path):
                    print(f"----> [{index + 1}/{len(resolver_result.https.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            if resolver_result.http is not None:
                print(f"HTTP Landing url: {resolver_result.http.url}")
                print(f"HTTP ScriptServer: {resolver_result.http.server}")
                print(f"HTTP IP: {resolver_result.http.ip.compressed}")
                print(f"Strict Transport Security: {resolver_result.http.hsts}")
                print(f"HTTP Redirection path:")
                for index, url in enumerate(resolver_result.http.redirection_path):
                    print(f"----> [{index + 1}/{len(resolver_result.http.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTP...")
            print()
        return final_results

    def resolve_script_site(self, script_site: str) -> LandingSiteResult:
        """
        This methods resolves landing of a script site.
        If an error occurs, it will be added in the error_logs attribute of the result, so exceptions are silent.

        :param script_site: A script site.
        :type script_site: str
        :return: A LandingSiteResult object.
        :rtype: LandingSiteResult
        """
        error_logs = list()
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(script_site, as_https=True)
            https_result = InnerLandingSiteSingleSchemeResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
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
            http_result = InnerLandingSiteSingleSchemeResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
        except Exception as exc:
            http_result = None
            error_logs.append(ErrorLog(exc, script_site, str(exc)))
        return LandingSiteResult(https_result, http_result, error_logs)

