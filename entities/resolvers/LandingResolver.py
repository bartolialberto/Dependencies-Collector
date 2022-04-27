from typing import Dict, Set
import requests
from entities.Url import Url
from entities.error_log.ErrorLog import ErrorLog
from entities.resolvers.DnsResolver import DnsResolver
from entities.resolvers.results.LandingSiteResult import LandingSiteResult
from entities.resolvers.results.LandingSiteSingleSchemeResult import LandingSiteSingleSchemeResult
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.UnknownReasonError import UnknownReasonError
from utils import requests_utils


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

    def resolve_sites(self, sites: Set[Url]) -> Dict[Url, LandingSiteResult]:
        """
        This methods resolves landing of all sites (web sites or script sites) parameters.

        :param sites: A set of sites, that are URLs.
        :type sites: Set[Url]
        :return: A dictionary with sites as keys and for each of them the corresponding landing result.
        :rtype: Dict[Url, LandingSiteResult]
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
                print(f"HTTPS Access Path: {resolver_result.https.a_path.stamp()}")
                print(f"Strict Transport Security: {resolver_result.https.hsts}")
                print(f"Landing scheme: {resolver_result.https.url.stamp_landing_scheme()}")
                print(f"HTTPS Redirection path:")
                for index, url in enumerate(resolver_result.https.redirection_path):
                    print(f"----> [{index + 1}/{len(resolver_result.https.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTPS...")

            # HTTP
            print(f"***** via HTTP *****")
            if resolver_result.http is not None:
                print(f"HTTP Landing url: {resolver_result.http.url}")
                print(f"HTTP Access Path: {resolver_result.http.a_path.stamp()}")
                print(f"Strict Transport Security: {resolver_result.http.hsts}")
                print(f"Landing scheme: {resolver_result.http.url.stamp_landing_scheme()}")
                print(f"HTTP Redirection path:")
                for index, url in enumerate(resolver_result.http.redirection_path):
                    print(f"----> [{index + 1}/{len(resolver_result.http.redirection_path)}]: {url}")
            else:
                print(f"Impossible to land somewhere via HTTP...")
            print()
        return final_results

    def resolve_site(self, url: Url) -> LandingSiteResult:
        """
        This methods resolves landing of a site, using HTTPS and HTTP as schemes.
        If an error occurs, it will be added in the error_logs attribute of the result and the result is set to None,
        so exceptions are silent.

        :param url: A site, that is an URL.
        :type url: Url
        :return: A LandingSiteResult object.
        :rtype: LandingSiteResult
        """
        error_logs = list()
        try:
            https_result = self.do_single_request(url, https=True)
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
            https_result = None
            error_logs.append(ErrorLog(e, url.https().string, str(e)))
        except requests.exceptions.ConnectionError as e:
            https_result = None
            error_logs.append(ErrorLog(e, url.https().string, str(e)))
        except Exception as exc:
            https_result = None
            error_logs.append(ErrorLog(exc, url.https().string, str(exc)))
        try:
            http_result = self.do_single_request(url, https=False)
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError) as e:
            http_result = None
            error_logs.append(ErrorLog(e, url.http().string, str(e)))
        except requests.exceptions.ConnectionError as e:
            http_result = None
            error_logs.append(ErrorLog(e, url.http().string, str(e)))
        except Exception as exc:
            http_result = None
            error_logs.append(ErrorLog(exc, url.http().string, str(exc)))
        return LandingSiteResult(https_result, http_result, error_logs)

    def do_single_request(self, site: Url, https: bool) -> LandingSiteSingleSchemeResult:
        """
        This methods actually executes a HTTP GET request; it constructs a HTTP URL from the site parameter using HTTPS
        or HTTP scheme according to the https parameter.

        :param site: An URL.
        :type site: Url
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
        :rtype: LandingSiteSingleSchemeResult
        """
        try:
            landing_url, redirection_path, hsts, ip = requests_utils.resolve_landing_page(site, as_https=https)
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
        try:
            a_path = self.dns_resolver.resolve_a_path(landing_url.domain_name())
        except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
            raise
        return LandingSiteSingleSchemeResult(landing_url, redirection_path, hsts, a_path)
