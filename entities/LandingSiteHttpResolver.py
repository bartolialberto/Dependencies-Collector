from typing import List
import requests
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from utils import domain_name_utils


class LandingSiteHttpResolver:
    landing_domain: str
    landing_url: str
    redirection_path: List[str]
    hsts: bool
    domain_redirection: bool

    def __init__(self, domain_name: str):
        self.redirection_path = list()
        try:
            domain_name_utils.grammatically_correct(domain_name)
        except InvalidDomainNameError:
            raise
        sts_is_present = False
        try:
            response = requests.get(domain_name_utils.deduct_url(domain_name, as_https=False))
            for resp in response.history:
                self.redirection_path.append(resp.url)
            # TODO: devo controllare anche tutte le pagine di redirection però... No?
            if response.headers.get('strict-transport-security') is not None:
                sts_is_present = True
            self.redirection_path.append(response.url)  # final page
            self.landing_url = response.url
            self.landing_domain = domain_name_utils.deduct_domain_name(response.url)
            if self.landing_domain != domain_name:
                self.domain_redirection = True
            else:
                self.domain_redirection = False
        except requests.exceptions.ConnectTimeout:  # The request timed out while trying to connect to the remote server. Requests that produced this error are safe to retry.
            raise
        except requests.exceptions.ConnectionError:  # A Connection error occurred. CASO IN CUI HTTPS NON E' SUPPORTATO
            raise
        except requests.exceptions.HTTPError:  # An HTTP error occurred.
            raise
        except requests.exceptions.URLRequired:  # A valid URL is required to make a request.
            raise
        except requests.exceptions.TooManyRedirects:  # Too many redirects.
            raise
        except requests.exceptions.ReadTimeout:  # The server did not send any data in the allotted amount of time.
            raise
        except requests.exceptions.Timeout:  # The request timed out. Catching this error will catch both ConnectTimeout and ReadTimeout errors.
            raise
        except requests.exceptions.RequestException:  # There was an ambiguous exception that occurred while handling your request.
            raise
        finally:
            self.hsts = sts_is_present
