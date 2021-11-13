from typing import List

import requests
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from utils import domain_name_utils


class LandingSiteHttpResolver:
    """
    This class concern is, given an url/domain name, to find the landing url while keeping tracks of all redirection
    happened. Start the request using http. An instance of this class already makes the elaboration in the initialization, no need to invoke
    particular methods. Thus, result can be returned from the attribute of such object.

    ...

    Instance Attributes
    -------------------
    landing_domain : `str`
        The domain of the landing url.
    landing_url : `str`
        The landing url.
    redirection_path : `list[str]`
        A list of all redirection.
    hsts : `bool`
        If HTTPS strict transport security header is set.
    domain_redirection : `bool`
        At the end if there is a domain redirection between the start and the end (landing).
    """

    def __init__(self, domain_name: str):
        """
        Initialize the object searching for the landing page from an url/domain name.

        :param domain_name: If this is an url, then it is used without any modification. If it is a domain name, then
        will be changed to a https url with that domain name.
        :type domain_name: str
        :raises InvalidDomainNameError: If the domain name is not valid (grammatically).
        :raises requests.exceptions.ConnectTimeout: The request timed out while trying to connect to the remote server.
        Requests that produced this error are safe to retry.
        :raises requests.exceptions.ConnectionError: A Connection error occurred. If https is not supported
        (server-side), this exception will be raised.
        :raises requests.exceptions.HTTPError: An HTTP error occurred.
        :raises requests.exceptions.URLRequired: A valid URL is required to make a request.
        :raises requests.exceptions.TooManyRedirects: Too many redirects.
        :raises requests.exceptions.ReadTimeout: The server did not send any data in the allotted amount of time.
        :raises requests.exceptions.Timeout: The request timed out. Catching this error will catch both ConnectTimeout
        and ReadTimeout errors.
        :raises requests.exceptions.RequestException: There was an ambiguous exception that occurred while handling
        your request.
        """
        self.redirection_path = list()
        try:
            domain_name_utils.grammatically_correct(domain_name)
        except InvalidDomainNameError:
            raise
        sts_is_present = False
        try:
            response = requests.get(domain_name_utils.deduct_http_url(domain_name, as_https=False))
            bool_list = list()
            for resp in response.history:
                self.redirection_path.append(resp.url)
                if resp.headers.get('strict-transport-security') is not None:
                    bool_list.append(True)
                else:
                    bool_list.append(False)
            for index, flag in enumerate(bool_list):
                if flag:
                    if index == len(bool_list) - 1:
                        sts_is_present = True
                    else:
                        pass
                else:
                    sts_is_present = False
                    break
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
