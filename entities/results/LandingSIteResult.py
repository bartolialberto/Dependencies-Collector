from ipaddress import IPv4Address
from typing import List
from entities.error_log.ErrorLog import ErrorLog
from utils import url_utils


class InnerLandingSiteSingleSchemeResult:
    def __init__(self, url: str, redirection_path: List[str], hsts: bool, ip: IPv4Address):
        self.url = url
        self.redirection_path = redirection_path
        self.hsts = hsts
        self.ip = ip
        self.server = url_utils.deduct_second_component(url)


class LandingSiteResult:
    def __init__(self, https_result: InnerLandingSiteSingleSchemeResult or None, http_result: InnerLandingSiteSingleSchemeResult or None, error_logs: List[ErrorLog]):
        self.https = https_result
        self.http = http_result
        self.error_logs = error_logs
