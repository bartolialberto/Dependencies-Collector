from typing import List, Dict, Set, Optional
from entities.DomainName import DomainName
from entities.Zone import Zone
from entities.error_log.ErrorLog import ErrorLog


class DnsZoneDependenciesResult:
    """
    This class represents the result of zone dependencies resolving. Such resolving is a bit tricky because it takes a
    domain name as input and then found such zone dependencies of such domain name; the problem is that we have to
    keep track also of zone dependencies of each zone and each name server found 'along' the resolving.
    Because of that this object comprehends multiple dictionaries to wrap everything in one object.

    ...

    Attributes
    ----------
    zone_dependencies : Set[Zone]
        The set of Zone (the application-defined object) which a domain depends upon.
    direct_zones : Dict[DomainName, Optional[Zone]]
        Name of the direct zone of the domain name.
    zone_dependencies_per_zone : Dict[DomainName, Set[Zone]]
        This dictionary associates each zone NAME (key) to a list of zone NAMEs which the (key) zone depends upon.
    zone_dependencies_per_name_server : Dict[DomainName, Set[Zone]]
        This dictionary associates each zone name server (key) to a list of zone NAMEs which the name server depends
        upon.
    error_logs : List[ErrorLog]
        A list of error logs occurred during resolving.
    """
    def __init__(self, zone_dependencies: Set[Zone], direct_zones: Dict[DomainName, Optional[Zone]], zone_dependencies_per_zone: Dict[Zone, Set[Zone]], zone_dependencies_per_name_server: Dict[DomainName, Set[Zone]], error_logs: List[ErrorLog]):
        """
        Initialize the object.

        :param zone_dependencies: A set of Zone (the application-defined object).
        :type zone_dependencies: Set[Zone]
        :param direct_zones: A zone name.
        :type direct_zones: Dict[DomainName, Optional[Zone]]
        :param zone_dependencies_per_zone: A dictionary that associate a zone name to a list of zone names.
        :type zone_dependencies_per_zone: Dict[DomainName, Set[Zone]]
        :param zone_dependencies_per_name_server: A dictionary that associate a name server to a list of zone names.
        :type zone_dependencies_per_name_server: Dict[DomainName, Set[Zone]]
        :param error_logs: A list of error logs.
        :type error_logs: List[ErrorLog]
        """
        self.zone_dependencies = zone_dependencies
        self.direct_zones = direct_zones
        self.zone_dependencies_per_zone = zone_dependencies_per_zone
        self.zone_dependencies_per_name_server = zone_dependencies_per_name_server
        self.error_logs = error_logs
