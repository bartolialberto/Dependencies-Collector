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

    def resolve_sites(self, sites: Set[str]) -> Dict[str, LandingSiteResult]:
        """
        This methods resolves landing of all sites (web sites or script sites) parameters.

        :param sites: A set of sites.
        :type sites: Set[str]
        :return: A dictionary with sites as keys and for each of them the corresponding result.
        :rtype: Dict[str, LandingSiteResult]
        """
        final_results = dict()
        for site in sites:
            print(f"Trying to resolve landing page of site: {site}")
            resolver_result = self.resolve_site(site)
            final_results[site] = resolver_result

            # HTTPS
            print(f"***** via HTTPS *****")
            if resolver_result.https is not None:
                print(f"HTTPS Landing url: {resolver_result.https.url}")
                print(f"HTTPS Server: {resolver_result.https.server}")
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

    def resolve_site(self, site: str) -> LandingSiteResult:
        """
        This methods resolves landing of a site.
        If an error occurs, it will be added in the error_logs attribute of the result, so exceptions are silent.

        :param site: A site.
        :type site: str
        :return: A LandingSiteResult object.
        :rtype: LandingSiteResult
        """
        error_logs = list()
        try:
            https_result = self.do_single_request(site, True)
        except requests.exceptions.ConnectionError as e:
            https_result = None
            error_logs.append(ErrorLog(e, site, str(e)))
        except Exception as exc:
            https_result = None
            error_logs.append(ErrorLog(exc, site, str(exc)))
        try:
            http_result = self.do_single_request(site, False)
        except requests.exceptions.ConnectionError as e:
            http_result = None
            error_logs.append(ErrorLog(e, site, str(e)))
        except Exception as exc:
            http_result = None
            error_logs.append(ErrorLog(exc, site, str(exc)))
        return LandingSiteResult(https_result, http_result, error_logs)
        """
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(site, as_https=True)
            https_result = InnerLandingSiteSingleSchemeResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
        except requests.exceptions.ConnectionError as e:
            # probably the server doesn't support HTTPS
            https_result = None
            error_logs.append(ErrorLog(e, site, str(e)))
        except Exception as exc:
            https_result = None
            error_logs.append(ErrorLog(exc, site, str(exc)))
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(site, as_https=False)
            http_result = InnerLandingSiteSingleSchemeResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
        except Exception as exc:
            http_result = None
            error_logs.append(ErrorLog(exc, site, str(exc)))
        return LandingSiteResult(https_result, http_result, error_logs)
        """

    def do_single_request(self, site: str, https: bool) -> InnerLandingSiteSingleSchemeResult:
        # TODO
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(site, as_https=https)
        except Exception:
            raise
        return InnerLandingSiteSingleSchemeResult(landing_url, redirection_path, hsts, IPv4Address(ip_string))
