from typing import List, Dict
from entities.Zone import Zone
from entities.error_log.ErrorLog import ErrorLog


class DnsZoneDependenciesResult:
    def __init__(self, zone_dependencies: List[Zone], zone_name_dependencies_per_zone: Dict[str, List[str]], zone_name_dependencies_per_name_server: Dict[str, List[str]], error_logs: List[ErrorLog]):
        self.zone_dependencies = zone_dependencies
        self.zone_name_dependencies_per_zone = zone_name_dependencies_per_zone
        self.zone_name_dependencies_per_name_server = zone_name_dependencies_per_name_server
        self.error_logs = error_logs
