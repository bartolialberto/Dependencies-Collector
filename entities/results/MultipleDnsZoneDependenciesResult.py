from entities.results.DnsZoneDependenciesResult import DnsZoneDependenciesResult
from utils import list_utils


class MultipleDnsZoneDependenciesResult:
    def __init__(self):
        self.zone_dependencies_per_domain_name = dict()
        self.zone_name_dependencies_per_zone = dict()
        self.zone_name_dependencies_per_name_server = dict()
        self.error_logs = list()

    def merge_single_resolver_result(self, domain_name: str, resolver_result: DnsZoneDependenciesResult):
        self.zone_dependencies_per_domain_name[domain_name] = resolver_result.zone_dependencies
        self.zone_name_dependencies_per_zone.update(resolver_result.zone_name_dependencies_per_zone)
        self.zone_name_dependencies_per_name_server.update(resolver_result.zone_name_dependencies_per_name_server)  # TODO: o questo? self.merge_zone_dependencies_per_nameserver_result(total_zone_dependencies_per_nameserver, temp_zone_dep_per_nameserver)
        for log in resolver_result.error_logs:
            self.error_logs.append(log)

    def merge(self, other: 'MultipleDnsZoneDependenciesResult'):
        MultipleDnsZoneDependenciesResult.merge_current_dict_to_total(self.zone_dependencies_per_domain_name, other.zone_dependencies_per_domain_name)
        MultipleDnsZoneDependenciesResult.merge_current_dict_to_total(self.zone_name_dependencies_per_zone, other.zone_name_dependencies_per_zone)
        MultipleDnsZoneDependenciesResult.merge_current_dict_to_total(self.zone_name_dependencies_per_name_server, other.zone_name_dependencies_per_name_server)

    @staticmethod
    def merge_current_dict_to_total(total_results_dict: dict, current_results_dict: dict) -> None:
        for key in current_results_dict.keys():
            try:
                total_results_dict[key]
            except KeyError:
                # total_results_dict[key] = current_results_dict[key]
                total_results_dict[key] = list()
            finally:
                for elem in current_results_dict[key]:
                    list_utils.append_with_no_duplicates(total_results_dict[key], elem)
