import csv
import ipaddress
from pathlib import Path
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
from persistence import helper_domain_name, helper_access, helper_alias, helper_ip_address, helper_autonomous_system, \
    helper_ip_range_tsv, helper_network_numbers, helper_rov, helper_prefixes_table, helper_ip_range_rov, \
    helper_ip_address_depends, helper_web_server, helper_web_site_lands, helper_ip_network, helper_script_server, \
    helper_script_site_lands, helper_script_withdraw, helper_script, helper_script_site
from persistence.BaseModel import NameServerEntity, IpAddressDependsAssociation, WebSiteLandsAssociation,\
    ScriptWithdrawAssociation, ScriptSiteLandsAssociation
from utils import network_utils, url_utils, file_utils, csv_utils


class DatabaseEntitiesCompleter:
    """
    This class represents the tool which concern is to recover all unresolved entities from database used as input.
    It needs all the resolvers of the application, so the only attribute is an instance of the application resolvers
    wrapper.

    ...

    Attributes
    ----------
    resolvers_wrapper : ApplicationResolversWrapper
        An in stance of the wrapper of all application resolvers.
    separator : str
        The string to use when dump the '.csv' file in the 'output' folder.
    """
    def __init__(self, resolvers_wrapper: ApplicationResolversWrapper, separator=';'):
        """
        Instantiate the object.

        :param resolvers_wrapper: The wrapper of all the application resolvers.
        :type resolvers_wrapper: ApplicationResolversWrapper
        """
        self.resolvers_wrapper = resolvers_wrapper
        self.separator = separator

    def do_complete_unresolved_entities(self, unresolved_entities: Set[UnresolvedEntityWrapper]) -> None:
        """
        This method is actually the one that executes (tries to execute) the completion of all unresolved entities.
        It also deals with the insertion in the database if there's new data resolved.

        :param unresolved_entities: All the unresolved entities.
        :type unresolved_entities: Set[UnresolvedEntityWrapper]
        """
        nse_list = list()
        wsla_https_list = list()
        wsla_http_list = list()
        ssla_https_list = list()
        ssla_http_list = list()
        iad_list = list()
        swas_list = list()
        for unresolved_entity in unresolved_entities:
            if unresolved_entity.cause == ResolvingErrorCauses.NAME_SERVER_WITHOUT_ACCESS_PATH:
                nse_list.append(unresolved_entity.entity)
            elif unresolved_entity.cause == ResolvingErrorCauses.NO_HTTPS_LANDING_FOR_WEB_SITE:
                wsla_https_list.append(unresolved_entity.entity)
            elif unresolved_entity.cause == ResolvingErrorCauses.NO_HTTP_LANDING_FOR_WEB_SITE:
                wsla_http_list.append(unresolved_entity.entity)
            elif unresolved_entity.cause == ResolvingErrorCauses.NO_HTTPS_LANDING_FOR_SCRIPT_SITE:
                ssla_https_list.append(unresolved_entity.entity)
            elif unresolved_entity.cause == ResolvingErrorCauses.NO_HTTP_LANDING_FOR_SCRIPT_SITE:
                ssla_http_list.append(unresolved_entity.entity)
            elif unresolved_entity.cause == ResolvingErrorCauses.INCOMPLETE_DEPENDENCIES_FOR_ADDRESS:
                iad_list.append(unresolved_entity.entity)
            elif unresolved_entity.cause == ResolvingErrorCauses.IMPOSSIBLE_TO_WITHDRAW_SCRIPT:
                swas_list.append(unresolved_entity.entity)
        self.do_complete_unresolved_name_servers(nse_list)
        self.do_complete_unresolved_web_sites_landing(wsla_https_list, is_https=True)
        self.do_complete_unresolved_web_sites_landing(wsla_http_list, is_https=False)
        self.do_complete_unresolved_script_sites_landing(ssla_https_list, True)
        self.do_complete_unresolved_script_sites_landing(ssla_http_list, False)
        self.do_complete_unresolved_ip_address_depends_association(iad_list)
        self.do_complete_not_withdrawn_scripts(swas_list)

    def do_complete_unresolved_name_servers(self, nses: List[NameServerEntity]) -> None:
        print(f"\nSTART UNRESOLVED NAME SERVERS ACCESS PATH RESOLVING")
        if len(nses) == 0:
            print(f"Nothing to do.\nEND UNRESOLVED NAME SERVERS ACCESS PATH RESOLVING")
            return
        for i, nse in enumerate(nses):
            try:
                rr_answer, rr_aliases = self.resolvers_wrapper.dns_resolver.do_query(nse.name.string, TypesRR.A)
            except (DomainNonExistentError, NoAnswerError, UnknownReasonError) as e:
                print(f"!!! {str(e)} !!!")
                self.resolvers_wrapper.error_logger.add_entry(ErrorLog(e, nse.name, str(e)))
                continue        # keep the relation as it is to keep the error info in the DB
            print(f"nameserver[{i+1}]: {nse.name.string} resolved in: {str(rr_answer.values)}")
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
            w_server_e, wse_dne = helper_web_server.insert(inner_result.server)
            iae = helper_ip_address.insert(inner_result.ip)
            predefined_network = network_utils.get_predefined_network(iae.exploded_notation)
            ine = helper_ip_network.insert(predefined_network)
            try:
                iada = helper_ip_address_depends.get_from_entity_ip_address(iae)
                helper_ip_address_depends.update_ip_network(iada, ine)
            except DoesNotExist:
                helper_ip_address_depends.insert(iae, ine, None, None)
            helper_web_site_lands.update(wsla_dict[web_site], w_server_e)
            print(f"for site: {web_site} now landing is: server={w_server_e.name.string}, IP address={iae.exploded_notation}")
        print(f"END UNRESOLVED WEB SITES LANDING RESOLUTION")

    def do_complete_unresolved_script_sites_landing(self, sslas: List[ScriptSiteLandsAssociation], is_https: bool):
        print(f"\n\nSTART UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
        if is_https:
            print(f"SCHEME USED: HTTPS")
        else:
            print(f"SCHEME USED: HTTP")
        if len(sslas) == 0:
            print(f"Nothing to do.\nEND UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
            return
        ssla_dict = dict()
        for ssla in sslas:
            ssla_dict[ssla.script_site.url.string] = ssla
        for script_site in ssla_dict.keys():
            try:
                inner_result = self.resolvers_wrapper.landing_resolver.do_single_request(script_site, is_https)
            except Exception:
                continue
            s_server_e, s_server_e_dne = helper_script_server.insert(inner_result.server)
            last_dne = s_server_e_dne
            for dn in inner_result.access_path[1:]:
                dne = helper_domain_name.insert(dn)
                last_dne = dne
            for ip in inner_result.ips:
                iae = helper_ip_address.insert(ip)
                helper_access.insert(last_dne, iae)
                predefined_network = network_utils.get_predefined_network(iae.exploded_notation)
                ine = helper_ip_network.insert(predefined_network)
                try:
                    iada = helper_ip_address_depends.get_from_entity_ip_address(iae)
                    helper_ip_address_depends.update_ip_network(iada, ine)
                except DoesNotExist:
                    helper_ip_address_depends.insert(iae, ine, None, None)
            helper_script_site_lands.update(ssla_dict[script_site], s_server_e)
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
                    ase = helper_autonomous_system.insert(entry.as_number, entry.as_description)

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

            if self.resolvers_wrapper.execute_rov_scraping and irre is None and ase is not None:
                try:
                    self.resolvers_wrapper.rov_page_scraper.load_as_page(ase.number)
                    row = self.resolvers_wrapper.rov_page_scraper.get_network_if_present(ip)
                    new_irre = helper_ip_range_rov.insert(row.prefix.compressed)
                    re = helper_rov.insert(row.rov_state.to_string(), row.visibility)
                    helper_prefixes_table.insert(new_irre, re, ase)
                    helper_ip_address_depends.update_ip_range_rov(iada, new_irre)
                    if tsv_modified:
                        print(f", ip_range_tsv is now resolved to {new_irre.compressed_notation}")
                    else:
                        print(f"--> for {ip.exploded}: ip_range_rov is now resolved to {new_irre.compressed_notation}")
                except (ValueError, TableNotPresentError, TableEmptyError, NotROVStateTypeError, NetworkNotFoundError, selenium.common.exceptions.WebDriverException):
                    if tsv_modified:
                        print("")
            else:
                pass
        print(f"END UNRESOLVED IP ADDRESS DEPENDENCIES RESOLUTION")

    def do_complete_not_withdrawn_scripts(self, swas: List[ScriptWithdrawAssociation]):
        print(f"\n\nSTART UNRESOLVED SCRIPT RESOLUTION")
        if len(swas) == 0:
            print(f"Nothing to do.\nEND UNRESOLVED SCRIPT RESOLUTION")
            return
        for swa in swas:
            if swa.https == True:
                url = url_utils.deduct_http_url(swa.web_site.url.string, as_https=True)
            else:
                url = url_utils.deduct_http_url(swa.web_site.url.string, as_https=False)
            try:
                scripts = self.resolvers_wrapper.script_resolver.search_script_application_dependencies(url)
                print(f"for: {swa.web_site.url.string} on https={swa.https} resolved {len(scripts)} scripts")
                for i, script in enumerate(scripts):
                    print(f"script[{i+1}]: integrity={script.integrity}, src={script.src}")
                    swa.delete_instance()
                    se = helper_script.insert(script.src)
                    helper_script_withdraw.insert(swa.web_site, se, swa.https, script.integrity)
                    s_site_e = helper_script_site.insert(url_utils.deduct_second_component(se.src))
                    try:
                        inner_result = self.resolvers_wrapper.landing_resolver.do_single_request(se.src, swa.https)
                    except Exception:
                        print(f"--> for script: src={script.src} it is impossible to resolve landing...")
                        helper_script_site_lands.insert(s_site_e, None, swa.https)
                        continue
                    s_server_e, s_server_e_dne = helper_script_server.insert(inner_result.server)
                    last_dne = s_server_e_dne
                    for dn in inner_result.access_path[1:]:
                        dne = helper_domain_name.insert(dn)
                        last_dne = dne
                    for ip in inner_result.ips:
                        iae = helper_ip_address.insert(ip)
                        helper_access.insert(last_dne, iae)
                        # TODO: e la question IP range per ogni address???
                    helper_script_site_lands.insert(s_site_e, s_server_e, swa.https)
                    print(f"--> for script: src={script.src} script server = {s_server_e.name.string}")
            except selenium.common.exceptions.WebDriverException:
                continue
        print(f"END UNRESOLVED SCRIPT RESOLUTION")

    @staticmethod
    def dump_unresolved_entities(unresolved_entities: Set[UnresolvedEntityWrapper], separator: str, project_root_directory=Path.cwd()) -> None:
        """
        This static method dumps all the unresolved entities parameter to a file in the 'output' subfolder of the
        project root directory parameter.
        Path.cwd() returns the current working directory which depends upon the entry point of the application; in
        particular, if we starts the application from the main.py file in the PRD, every time Path.cwd() is encountered
        (even in methods belonging to files that are in sub-folders with respect to PRD) then the actual PRD is returned.
        If the application is started from a file that belongs to the entities package, then Path.cwd() will return the
        entities sub-folder with respect to the PRD. So to give a bit of modularity, the PRD parameter is set to default
        as if the entry point is main.py file (which is the only entry point considered).

        :param unresolved_entities: A set containing all the unresolved entities.
        :type unresolved_entities: Set[UnresolvedEntityWrapper]
        :param separator: The separator to use in the .csv file.
        :type separator: str
        :param project_root_directory: The Path object pointing at the project root directory.
        :type project_root_directory: Path
        """
        file = file_utils.set_file_in_folder('output', 'dump_unresolved_entities.csv', project_root_directory=project_root_directory)
        with file.open('w', encoding='utf-8', newline='') as f:
            write = csv.writer(f, dialect=csv_utils.return_personalized_dialect_name(f"{separator}"))
            for unresolved_entity in unresolved_entities:
                temp_list = list()
                temp_list.append(str(unresolved_entity.cause))
                temp_list.append(str(type(unresolved_entity.entity))+'='+str(unresolved_entity.entity))
                temp_list.append(str(type(unresolved_entity.entity_cause))+'='+str(unresolved_entity.entity_cause))
                write.writerow(temp_list)
            f.close()

