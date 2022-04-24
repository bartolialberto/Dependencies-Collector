from entities.DomainName import DomainName
from entities.resolvers.results.DnsZoneDependenciesResult import DnsZoneDependenciesResult
from utils import dict_utils


class MultipleDnsZoneDependenciesResult:
    """
    This class represents the result of multiple zone dependencies resolving.
    Such resolving is a bit tricky because it takes a list of domain names as input and then found such zone
    dependencies of such domain names; the problem is that we have to keep track also of zone dependencies of each zone
    and each name server found 'along' the resolving. Because of that this object comprehends 3 dictionaries.
    The difference between this object and a DnsZoneDependenciesResult one, is that here the Zone
    (the application-defined object) dependencies takes form in a dictionary that associates each domain to a set of
    Zone (the application-defined object) dependencies.

    ...

    Attributes
    ----------
    zone_dependencies_per_domain_name : Dict[DomainName, Set[Zone]]
        This dictionary associates each domain name to a set of Zone which the domain name depends upon.
    direct_zones : Dict[DomainName, Optional[Zone]]
        This dictionary associates each domain name with its direct Zone.
    zone_dependencies_per_zone : Dict[Zone, Set[Zone]]
        This dictionary associates each zone to a set of Zone which the first zone depends upon.
    zone_dependencies_per_name_server : Dict[DomainName, Set[Zone]]
        This dictionary associates each zone name server to a set of Zone which name server depends upon.
    error_logs : List[ErrorLog]
        A list of error logs occurred during resolving.
    """
    def __init__(self):
        """
        Initialize the object.

        """
        self.zone_dependencies_per_domain_name = dict()
        self.direct_zones = dict()
        self.zone_dependencies_per_zone = dict()
        self.zone_dependencies_per_name_server = dict()
        self.error_logs = list()

    def join_single_resolver_result(self, domain_name: DomainName, resolver_result: DnsZoneDependenciesResult):
        """
        This method incorporates the result of a single zone dependency resolution into the self object.

        :param domain_name: The domain name associated to the resolution.
        :type domain_name: str
        :param resolver_result: A DnsZoneDependenciesResult object.
        :type resolver_result: DnsZoneDependenciesResult
        """
        self.zone_dependencies_per_domain_name[domain_name] = resolver_result.zone_dependencies
        self.direct_zones.update(resolver_result.direct_zones)
        self.zone_dependencies_per_zone.update(resolver_result.zone_dependencies_per_zone)
        self.zone_dependencies_per_name_server.update(resolver_result.zone_dependencies_per_name_server)
        for log in resolver_result.error_logs:
            self.error_logs.append(log)

    def merge(self, other: 'MultipleDnsZoneDependenciesResult'):        # FORWARD DECLARATIONS (REFERENCES)
        """
        This method merge all the infos contained in another MultipleDnsZoneDependenciesResult object into the self one.

        :param other: Another MultipleDnsZoneDependenciesResult object.
        :type other: MultipleDnsZoneDependenciesResult
        """
        dict_utils.merge_current_dict_with_set_values_to_total(self.zone_dependencies_per_domain_name, other.zone_dependencies_per_domain_name)
        dict_utils.merge_current_dict_to_total(self.direct_zones, other.direct_zones)
        dict_utils.merge_current_dict_with_set_values_to_total(self.zone_dependencies_per_zone, other.zone_dependencies_per_zone)
        dict_utils.merge_current_dict_with_set_values_to_total(self.zone_dependencies_per_name_server, other.zone_dependencies_per_name_server)
