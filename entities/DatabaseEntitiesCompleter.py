import ipaddress
from typing import List, Set, Tuple
import selenium
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.UnresolvedEntityWrapper import UnresolvedEntityWrapper
from entities.enums.ResolvingErrorCauses import ResolvingErrorCauses
from entities.enums.TypesRR import TypesRR
from entities.error_log.ErrorLog import ErrorLog
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError
from exceptions.UnknownReasonError import UnknownReasonError
from persistence import helper_domain_name, helper_access, helper_alias, helper_ip_address, \
    helper_application_results, helper_autonomous_system, helper_ip_range_tsv, helper_network_numbers,\
    helper_ip_address_depends, helper_rov, helper_prefixes_table, helper_ip_range_rov
from persistence.BaseModel import NameServerEntity, WebSiteEntity, ScriptSiteEntity, IpAddressDependsAssociation, \
    AutonomousSystemEntity, IpAddressEntity


# TODO
class DatabaseEntitiesCompleter:
    def __init__(self, resolvers_wrapper: ApplicationResolversWrapper):
        self.resolvers_wrapper = resolvers_wrapper

    def do_complete_unresolved_entities(self, entities: Set[UnresolvedEntityWrapper]):
        nse_list = list()
        wse_list = list()
        sse_list = list()
        iad_list = list()
        for elem in entities:
            if elem.cause == ResolvingErrorCauses.NAME_SERVER_WITHOUT_ACCESS_PATH:
                nse_list.append(elem.entity)
            elif elem.cause == ResolvingErrorCauses.NO_LANDING_FOR_WEB_SITE:
                wse_list.append(elem.entity)
            elif elem.cause == ResolvingErrorCauses.NO_LANDING_FOR_SCRIPT_SITE:
                sse_list.append(elem.entity)
            elif elem.cause == ResolvingErrorCauses.INCOMPLETE_DEPENDENCIES_FOR_ADDRESS:
                iad_list.append(elem.entity)

        self.do_complete_unresolved_name_servers(nse_list)
        self.do_complete_unresolved_web_sites_landing(wse_list)
        self.do_complete_unresolved_script_sites_landing(sse_list)
        self.do_complete_unresolved_ip_address_depends_association(iad_list)

    def do_complete_unresolved_name_servers(self, nses: List[NameServerEntity]):
        print(f"\nSTART UNRESOLVED NAME SERVERS ACCESS PATH RESOLVING")
        if len(nses) == 0:
            print(f"Nothing to do.\nEND UNRESOLVED NAME SERVERS ACCESS PATH RESOLVING")
            return
        for i, nse in enumerate(nses):
            try:
                rr_answer, rr_aliases = self.resolvers_wrapper.dns_resolver.do_query(nse.name, TypesRR.A)
            except (DomainNonExistentError, NoAnswerError, UnknownReasonError) as e:
                print(f"!!! {str(e)} !!!")
                self.resolvers_wrapper.error_logger.add_entry(ErrorLog(e, nse.name, str(e)))
                continue        # keep the relation as it is to keep the error info in the DB
            print(f"nameserver[{i+1}]: {nse.name} resolved in: {str(rr_answer.values)}")
            helper_access.delete_of_entity_domain_name(nse.name)
            for rr in rr_aliases:
                name_dne = helper_domain_name.insert(rr.name)
                alias_dne = helper_domain_name.insert(rr.get_first_value())
                helper_alias.insert(name_dne, alias_dne)
            dne = helper_domain_name.insert(rr_answer.name)
            for val in rr_answer.values:
                iae = helper_ip_address.insert(val)
                helper_access.insert(dne, iae)
        print(f"END UNRESOLVED NAME SERVERS ACCESS PATH RESOLVING")

    def do_complete_unresolved_web_sites_landing(self, wses: List[WebSiteEntity]):
        print(f"\n\nSTART UNRESOLVED WEB SITES LANDING RESOLUTION")
        if len(wses) == 0:
            print(f"Nothing to do.\nEND UNRESOLVED WEB SITES LANDING RESOLUTION")
            return
        web_sites = set(map(lambda wse: wse.url, wses))
        results = self.resolvers_wrapper.landing_resolver.resolve_sites(web_sites)
        for web_site in results.keys():
            self.resolvers_wrapper.error_logger.add_entries(results[web_site].error_logs)
        helper_application_results.insert_landing_web_sites_results(results)    # takes care of deleting previous ones and inserts the new ones: either if resolution went well or bad
        print(f"END UNRESOLVED WEB SITES LANDING RESOLUTION")

    def do_complete_unresolved_script_sites_landing(self, sses: List[ScriptSiteEntity]):
        print(f"\n\nSTART UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
        if len(sses) == 0:
            print(f"Nothing to do.\nEND UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
            return
        script_sites = set(map(lambda sse: sse.url, sses))
        results = self.resolvers_wrapper.landing_resolver.resolve_sites(script_sites)
        for script_site in results.keys():
            self.resolvers_wrapper.error_logger.add_entries(results[script_site].error_logs)
        helper_application_results.insert_landing_script_sites_results(results)    # takes care of deleting previous ones and inserts the new ones: either if resolution went well or bad
        print(f"END UNRESOLVED SCRIPT SITES LANDING RESOLUTION")

    def do_complete_unresolved_ip_address_depends_association(self, iadas: List[IpAddressDependsAssociation]):
        print(f"\n\nSTART UNRESOLVED IP ADDRESS DEPENDENCIES RESOLUTION")
        if len(iadas) == 0:
            print(f"Nothing to do.\nEND UNRESOLVED IP ADDRESS DEPENDENCIES RESOLUTION")
            return
        for iada in iadas:
            ip = ipaddress.IPv4Address(iada.ip_address.exploded_notation)
            iae = iada.ip_address
            network = ipaddress.IPv4Network(iada.ip_network.compressed_notation)
            ine = iada.ip_network
            irte = iada.ip_range_tsv
            irre = iada.ip_range_rov
            helper_ip_address_depends.delete_by_id(iada.get_id())
            as_number = None
            ase = None
            if iada.ip_range_tsv is None:
                try:
                    entry = self.resolvers_wrapper.ip_as_database.resolve_range(ip)
                    as_number = entry.as_number
                    ase = helper_autonomous_system.insert(entry.as_number)

                    belonging_network, networks = entry.get_network_of_ip(ip)     # it cannot happen that the entry is found but not the network ==> no exceptions are catched
                    new_irte = helper_ip_range_tsv.insert(belonging_network.compressed)
                    helper_network_numbers.insert(new_irte, ase)
                except (ValueError, TypeError, AutonomousSystemNotFoundError):
                    new_irte = None
            else:
                new_irte = irte

            if iada.ip_range_rov is None and as_number is not None:
                try:
                    self.resolvers_wrapper.rov_page_scraper.load_as_page(as_number)
                    row = self.resolvers_wrapper.rov_page_scraper.get_network_if_present(ip)
                    new_irre = helper_ip_range_rov.insert(row.prefix.compressed)
                    re = helper_rov.insert(row.rov_state.to_string(), row.visibility)
                    helper_prefixes_table.insert(irre, re, ase)
                except (ValueError, TableNotPresentError, TableEmptyError, NotROVStateTypeError, NetworkNotFoundError, selenium.common.exceptions.WebDriverException):
                    new_irre = None
            else:
                new_irre = irre

            print(f"--> for: {ip.exploded} resolved ip_range_tsv={new_irte} and ip_range_rov={new_irre}")
            helper_ip_address_depends.insert(iae, ine, new_irte, new_irre)
        print(f"END UNRESOLVED IP ADDRESS DEPENDENCIES RESOLUTION")

