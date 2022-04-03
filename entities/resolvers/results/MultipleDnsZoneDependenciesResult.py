from entities.DomainName import DomainName
from entities.resolvers.results.DnsZoneDependenciesResult import DnsZoneDependenciesResult
from utils import list_utils


class MultipleDnsZoneDependenciesResult:
    """
    This class represents the result of multiple zone dependencies resolving.
    Such resolving is a bit tricky because it takes a list of domain names as input and then found such zone
    dependencies of such domain names; the problem is that we have to keep track also of zone dependencies of each zone
    and each name server found 'along' the resolving. Because of that this object comprehends 3 dictionaries.
    The difference between this object and a DnsZoneDependenciesResult one, is that here the Zone
    (the application-defined object) dependencies takes form in a dictionary that associates each domain to a list of
    Zone (the application-defined object) dependencies.

    ...

    Attributes
    ----------
    zone_dependencies_per_domain_name : Dict[str, List[Zone]]
        This dictionary associates each domain name to a list of Zone (the application-defined object) which the domain
        name depends upon.
    direct_zone_per_domain_name : Dict[str, str]
        This dictionary associates each domain with its direct zone name.
    zone_dependencies_per_zone : Dict[str, List[str]]
        This dictionary associates each zone NAME (key) to a list of zone NAMEs which the (key) zone depends upon.
    zone_dependencies_per_name_server : Dict[str, List[str]]
        This dictionary associates each zone name server (key) to a list of zone NAMEs which the name server depends
        upon.
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

    def merge_single_resolver_result(self, domain_name: DomainName, resolver_result: DnsZoneDependenciesResult):
        """
        This method incorporates the result of a single zone dependency resolution into the self object.

        :param domain_name: The domain name associated to the resolution.
        :type domain_name: str
        :param resolver_result: A DnsZoneDependenciesResult object.
        :type resolver_result: DnsZoneDependenciesResult
        """
        self.zone_dependencies_per_domain_name[domain_name] = resolver_result.zone_dependencies
        # self.direct_zone_per_domain_name[domain_name] = resolver_result.direct_zones
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
        MultipleDnsZoneDependenciesResult.merge_current_dict_with_list_values_to_total(self.zone_dependencies_per_domain_name, other.zone_dependencies_per_domain_name)
        MultipleDnsZoneDependenciesResult.merge_current_dict_to_total(self.direct_zones, other.direct_zones)
        MultipleDnsZoneDependenciesResult.merge_current_dict_with_list_values_to_total(self.zone_dependencies_per_zone, other.zone_dependencies_per_zone)
        MultipleDnsZoneDependenciesResult.merge_current_dict_with_list_values_to_total(self.zone_dependencies_per_name_server, other.zone_dependencies_per_name_server)

    @staticmethod
    def merge_current_dict_to_total(total_results_dict: dict, current_results_dict: dict) -> None:
        """
        This static method merges a dictionary into another dictionary.
        It is an auxiliary method.

        :param total_results_dict: The dictionary that takes the infos of the other.
        :type total_results_dict: dict
        :param current_results_dict: The dictionary which all the infos are taken.
        :type current_results_dict: dict
        """
        for key in current_results_dict.keys():
            total_results_dict[key] = current_results_dict[key]

    @staticmethod
    def merge_current_dict_with_list_values_to_total(total_results_dict: dict, current_results_dict: dict) -> None:
        """
        This static method merges a dictionary into another dictionary following the structure of the
        MultipleDnsZoneDependenciesResult dictionaries attributes.
        It is an auxiliary method.

        :param total_results_dict: The dictionary that takes the infos of the other.
        :type total_results_dict: dict
        :param current_results_dict: The dictionary which all the infos are taken.
        :type current_results_dict: dict
        """
        for key in current_results_dict.keys():
            try:
                total_results_dict[key]
            except KeyError:
                total_results_dict[key] = list()
            finally:
                for elem in current_results_dict[key]:
                    list_utils.append_with_no_duplicates(total_results_dict[key], elem)
