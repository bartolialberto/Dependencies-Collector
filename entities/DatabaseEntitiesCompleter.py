import ipaddress
from typing import List, Set
import selenium
from peewee import DoesNotExist
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
from persistence import helper_domain_name, helper_access, helper_alias, helper_ip_address, helper_autonomous_system,\
    helper_ip_range_tsv, helper_network_numbers, helper_rov, helper_prefixes_table, helper_ip_range_rov,\
    helper_ip_address_depends, helper_web_server, helper_web_site_lands, helper_ip_network, helper_script_server,\
    helper_script_site_lands
from persistence.BaseModel import NameServerEntity, WebSiteEntity, ScriptSiteEntity, IpAddressDependsAssociation, \
    WebSiteLandsAssociation
from utils import network_utils


class DatabaseEntitiesCompleter:
    def __init__(self, resolvers_wrapper: ApplicationResolversWrapper):
        self.resolvers_wrapper = resolvers_wrapper

    def do_complete_unresolved_entities(self, unresolved_entities: Set[UnresolvedEntityWrapper]):
        nse_list = list()
        wsla_https_list = list()
        wsla_http_list = list()
        sse_https_list = list()
        sse_http_list = list()
        iad_list = list()
        for entity in unresolved_entities:
            if entity.cause == ResolvingErrorCauses.NAME_SERVER_WITHOUT_ACCESS_PATH:
                nse_list.append(entity.entity)
            elif entity.cause == ResolvingErrorCauses.NO_HTTPS_LANDING_FOR_WEB_SITE:
                wsla_https_list.append(entity.entity)
            elif entity.cause == ResolvingErrorCauses.NO_HTTP_LANDING_FOR_WEB_SITE:
                wsla_http_list.append(entity.entity)
            elif entity.cause == ResolvingErrorCauses.NO_HTTPS_LANDING_FOR_SCRIPT_SITE:
                sse_https_list.append(entity.entity)
            elif entity.cause == ResolvingErrorCauses.NO_HTTP_LANDING_FOR_SCRIPT_SITE:
                sse_http_list.append(entity.entity)
            elif entity.cause == ResolvingErrorCauses.INCOMPLETE_DEPENDENCIES_FOR_ADDRESS:
                iad_list.append(entity.entity)
        self.do_complete_unresolved_name_servers(nse_list)
        self.do_complete_unresolved_web_sites_landing(wsla_https_list, is_https=True)
        self.do_complete_unresolved_web_sites_landing(wsla_http_list, is_https=False)
        self.do_complete_unresolved_script_sites_landing(sse_https_list, True)
        self.do_complete_unresolved_script_sites_landing(sse_http_list, False)
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

    def do_complete_unresolved_web_sites_landing(self, wslas: List[WebSiteLandsAssociation], is_https: bool):
        print(f"\n\nSTART UNRESOLVED WEB SITES LANDING RESOLUTION")
        if is_https:
            print(f"SCHEME USED: HTTPS")
        else:
            print(f"SCHEME USED: HTTP")
        if len(wslas) == 0:
            print(f"Nothing to do.\nEND UNRESOLVED WEB SITES LANDING RESOLUTION")
            return
        wsla_dict = dict()
        for wsla in wslas:
            wsla_dict[wsla.web_site.url.string] = wsla
        for web_site in wsla_dict.keys():
            try:
                inner_result = self.resolvers_wrapper.landing_resolver.do_single_request(web_site, is_https)
            except Exception:
                continue
            w_server_e = helper_web_server.insert(inner_result.server)
            iae = helper_ip_address.insert(inner_result.ip)
            predefined_network = network_utils.get_predefined_network(iae.exploded_notation)
            ine = helper_ip_network.insert(predefined_network)
            try:
                iada = helper_ip_address_depends.get_from_entity_ip_address(iae)
                helper_ip_address_depends.update_ip_network(iada, ine)
            except DoesNotExist:
                helper_ip_address_depends.insert(iae, ine, None, None)
            helper_web_site_lands.update(wsla_dict[web_site], w_server_e, iae)
            print(f"for site: {web_site} now landing is: server={w_server_e.name.name}, IP address={iae.exploded_notation}")
        print(f"END UNRESOLVED WEB SITES LANDING RESOLUTION")

    def do_complete_unresolved_script_sites_landing(self, https_sses: List[ScriptSiteEntity], is_https: bool):
        print(f"\n\nSTART UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
        if is_https:
            print(f"SCHEME USED: HTTPS")
        else:
            print(f"SCHEME USED: HTTP")
        if len(https_sses) == 0:
            print(f"Nothing to do.\nEND UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
            return
        sse_dict = dict()
        for sse in https_sses:
            sse_dict[sse.url] = sse
        for script_site in sse_dict.keys():
            try:
                inner_result = self.resolvers_wrapper.landing_resolver.do_single_request(script_site, is_https)
            except Exception:
                continue
            s_server_e = helper_script_server.insert(inner_result.server)
            iae = helper_ip_address.insert(inner_result.ip)
            predefined_network = network_utils.get_predefined_network(iae.exploded_notation)
            ine = helper_ip_network.insert(predefined_network)
            try:
                iada = helper_ip_address_depends.get_from_entity_ip_address(iae)
                helper_ip_address_depends.update_ip_network(iada, ine)
            except DoesNotExist:
                helper_ip_address_depends.insert(iae, ine, None, None)
            helper_script_site_lands.insert(sse_dict[script_site], s_server_e, is_https, iae)
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
            tsv_modified = False

            if irte is None:
                try:
                    entry = self.resolvers_wrapper.ip_as_database.resolve_range(ip)
                    ase = helper_autonomous_system.insert(entry.as_number)

                    belonging_network, networks = entry.get_network_of_ip(ip)  # it cannot happen that the entry is found but not the network ==> no exceptions are catched
                    new_irte = helper_ip_range_tsv.insert(belonging_network.compressed)
                    helper_network_numbers.insert(new_irte, ase)
                    helper_ip_address_depends.update_ip_range_tsv(iada, new_irte)
                    print(f"--> for {ip.exploded}: ip_range_tsv is now resolved to {new_irte.compressed_notation}", end="")
                    tsv_modified = True
                except (ValueError, TypeError, AutonomousSystemNotFoundError):
                    ase = None
            else:
                try:
                    ase = helper_autonomous_system.get_of_entity_ip_range_tsv(irte)
                except DoesNotExist:
                    ase = None

            if irre is None and ase is not None:
                try:
                    self.resolvers_wrapper.rov_page_scraper.load_as_page(ase.number)
                    row = self.resolvers_wrapper.rov_page_scraper.get_network_if_present(ip)
                    new_irre = helper_ip_range_rov.insert(row.prefix.compressed)
                    re = helper_rov.insert(row.rov_state.to_string(), row.visibility)
                    helper_prefixes_table.insert(irre, re, ase)
                    helper_ip_address_depends.update_ip_range_rov(iada, new_irre)
                    if tsv_modified:
                        print(f", ip_range_tsv is now resolved to {new_irre.compressed_notation}")
                    else:
                        print(f"--> for {ip.exploded}: ip_range_rov is now resolved to {new_irre.compressed_notation}")
                except (ValueError, TableNotPresentError, TableEmptyError, NotROVStateTypeError, NetworkNotFoundError, selenium.common.exceptions.WebDriverException):
                    if tsv_modified:
                        print("")
            else:
                print("")
        print(f"END UNRESOLVED IP ADDRESS DEPENDENCIES RESOLUTION")

