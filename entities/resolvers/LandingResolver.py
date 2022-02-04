import ipaddress
from ipaddress import IPv4Address
from typing import Dict, Set
import requests
from entities.error_log.ErrorLog import ErrorLog
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.results.LandingSiteResult import LandingSiteResult, InnerLandingSiteSingleSchemeResult
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.UnknownReasonError import UnknownReasonError
from utils import requests_utils, domain_name_utils, url_utils


class LandingResolver:
    """
    This class' concern is to provide tools to resolve URL landing.

    ...

    Attributes
    ----------
    dns_resolver : DnsResolver
        A DNS resolver.
    """
    def __init__(self, dns_resolver: DnsResolver):
        """
        Instantiate the object.

        :param dns_resolver: A DNS resolver.
        :type dns_resolver: DnsResolver
        """
        self.dns_resolver = dns_resolver

    def resolve_sites(self, sites: Set[str]) -> Dict[str, LandingSiteResult]:
        """
        This methods resolves landing of all sites (web sites or script sites) parameters.

        :param sites: A set of sites.
        :type sites: Set[str]
        :return: A dictionary with sites as keys and for each of them the corresponding result.
        :rtype: Dict[str, LandingSiteResult]
        """
        final_results = dict()
        for i, site in enumerate(sites):
            print(f"Trying to resolve landing page of site[{i+1}/{len(sites)}]: {site}")
            resolver_result = self.resolve_site(site)
            final_results[site] = resolver_result

            # HTTPS
            print(f"***** via HTTPS *****")
            if resolver_result.https is not None:
                print(f"HTTPS Landing url: {resolver_result.https.url}")
                print(f"HTTPS Access Path: {resolver_result.https.stamp_access_path()}")
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
                print(f"HTTP Access Path: {resolver_result.http.stamp_access_path()}")
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
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
            https_result = None
            error_logs.append(ErrorLog(e, site, str(e)))
        except requests.exceptions.ConnectionError as e:
            https_result = None
            error_logs.append(ErrorLog(e, site, str(e)))
        except Exception as exc:
            https_result = None
            error_logs.append(ErrorLog(exc, site, str(exc)))
        try:
            http_result = self.do_single_request(site, False)
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
            http_result = None
            error_logs.append(ErrorLog(e, site, str(e)))
        except requests.exceptions.ConnectionError as e:
            http_result = None
            error_logs.append(ErrorLog(e, site, str(e)))
        except Exception as exc:
            http_result = None
            error_logs.append(ErrorLog(exc, site, str(exc)))
        return LandingSiteResult(https_result, http_result, error_logs)

    def do_single_request(self, site: str, https: bool) -> InnerLandingSiteSingleSchemeResult:
        """
        This methods actually executes a HTTP GET request; it constructs a HTTP URL from the site parameter using HTTPS
        or HTTP scheme according to the https parameter.

        :param site: A site string.
        :type site: str
        :param https: A flag to set the scheme used: HTTPS or HTTP.
        :type https: bool
        :raise requests.exceptions.ConnectTimeout: The request timed out while trying to connect to the remote server.
        Requests that produced this error are safe to retry.
        :raise requests.exceptions.ConnectionError: A Connection error occurred. This occurs if https is not supported
        by the server.
        :raise requests.exceptions.URLRequired: A valid URL is required to make a request.
        :raise requests.exceptions.TooManyRedirects: Too many redirects.
        :raise requests.exceptions.ReadTimeout: The server did not send any data in the allotted amount of time.
        :raise requests.exceptions.Timeout: The request timed out. Catching this error will catch both ConnectTimeout
        and ReadTimeout errors.
        :raise requests.exceptions.RequestException: There was an ambiguous exception that occurred while handling your
        :return: A InnerLandingSiteSingleSchemeResult object.
        :rtype: InnerLandingSiteSingleSchemeResult
        """
        try:
            landing_url, redirection_path, hsts, ip_string = requests_utils.resolve_landing_page(site, as_https=https)
        except requests.exceptions.ConnectTimeout:
            # The request timed out while trying to connect to the remote server.
            # Requests that produced this error are safe to retry.
            raise
        except requests.exceptions.ConnectionError:
            # A Connection error occurred. This occurs if https is not supported by the server
            raise
        except requests.exceptions.HTTPError:
            # An HTTP error occurred.
            raise
        except requests.exceptions.URLRequired:
            # A valid URL is required to make a request.
            raise
        except requests.exceptions.InvalidURL:
            raise
        except requests.exceptions.TooManyRedirects:
            # Too many redirects.
            raise
        except requests.exceptions.ReadTimeout:
            # The server did not send any data in the allotted amount of time.
            raise
        except requests.exceptions.Timeout:
            # The request timed out. Catching this error will catch both ConnectTimeout and ReadTimeout errors.
            raise
        except requests.exceptions.RequestException:
            # There was an ambiguous exception that occurred while handling your request.
            raise
        access_path = list()
        ip_set = set()
        web_server_domain_name = domain_name_utils.deduct_domain_name(landing_url, with_trailing_point=True)
        try:
            rr_a, rr_cnames = self.dns_resolver.resolve_access_path(web_server_domain_name)
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
            raise
        for rr in rr_cnames:
            access_path.append(rr.name)
        access_path.append(rr_a.name)
        for value in rr_a.values:
            ip_set.add(ipaddress.IPv4Address(value))
        return InnerLandingSiteSingleSchemeResult(landing_url, redirection_path, hsts, ip_set, access_path)
