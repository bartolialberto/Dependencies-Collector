import csv
import ipaddress
from pathlib import Path
from typing import List, Set
import selenium
from peewee import DoesNotExist
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.DomainName import DomainName
from entities.SchemeUrl import SchemeUrl
from entities.UnresolvedEntityWrapper import UnresolvedEntityWrapper
from entities.Url import Url
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
    helper_script_site_lands, helper_script_withdraw, helper_script, helper_script_site, helper_mail_domain_composed, \
    helper_mail_server, helper_paths
from persistence.BaseModel import NameServerEntity, IpAddressDependsAssociation, WebSiteLandsAssociation, \
    ScriptWithdrawAssociation, ScriptSiteLandsAssociation, MailDomainComposedAssociation, AccessAssociation, \
    DomainNameEntity
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

    def do_complete_unresolved_entities(self, unresolved_entities: set) -> None:
        """
        This method is actually the one that executes (tries to execute) the completion of all unresolved entities.
        It also deals with the insertion in the database if there's new data resolved.

        :param unresolved_entities: All the unresolved entities.
        :type unresolved_entities: Set[UnresolvedEntityWrapper]
        """
        wslas = list()
        swas = list()
        sslas = list()
        aas = list()
        mdcas = list()
        iadas = list()
        for unresolved_entity in unresolved_entities:
            if isinstance(unresolved_entity, WebSiteLandsAssociation):
                wslas.append(unresolved_entity)
            elif isinstance(unresolved_entity, ScriptWithdrawAssociation):
                swas.append(unresolved_entity)
            elif isinstance(unresolved_entity, ScriptSiteLandsAssociation):
                sslas.append(unresolved_entity)
            elif isinstance(unresolved_entity, AccessAssociation):
                aas.append(unresolved_entity)

            #
            elif isinstance(unresolved_entity, MailDomainComposedAssociation):
                mdcas.append(unresolved_entity)

            elif isinstance(unresolved_entity, IpAddressDependsAssociation):
                iadas.append(unresolved_entity)
            else:
                raise ValueError
        self.do_complete_unresolved_web_sites_landing(wslas)
        self.do_complete_domain_names_with_no_access(aas)
        self.do_complete_unresolved_web_sites_scripts_withdraw(swas)
        self.do_complete_unresolved_script_sites_landing(sslas)
        self.do_complete_unresolved_mail_domain(mdcas)

    def do_complete_domain_names_with_no_access(self, aas: List[AccessAssociation]) -> None:
        if len(aas) == 0:
            return
        print(f"\nSTART DOMAIN NAME WITH NO ACCESS RESOLVING")
        for i, aa in enumerate(aas):
            domain_name = DomainName(aa.domain_name.string)
            print(f"association[{i+1}/{len(aas)}]: ", end='')
            try:
                a_path = self.resolvers_wrapper.dns_resolver.resolve_access_path(domain_name)
            except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                print(f"{domain_name} not resolved...")
                continue
            print(f"{a_path.stamp()}")
            helper_paths.insert_a_path(a_path)
            aa.delete_instance()
        print(f"END DOMAIN NAME WITH NO ACCESS RESOLVING")

    def do_complete_unresolved_web_sites_landing(self, wslas: List[WebSiteLandsAssociation]) -> None:
        if len(wslas) == 0:
            return
        print(f"\n\nSTART UNRESOLVED WEB SITES LANDING RESOLUTION")
        for i, wsla in enumerate(wslas):
            site = Url(wsla.web_site)
            https = bool(wsla.starting_https)
            print(f"association[{i+1}/{len(wslas)}]: scheme={https}, url={site}")
            try:
                result = self.resolvers_wrapper.landing_resolver.do_single_request(site, https)
            except Exception:
                print(f"--> Can't resolve landing...")
                continue
            print(f"--> Landed on: {result.url}")
            server_entity = helper_web_server.insert(result.server)
            helper_web_site_lands.insert(wsla.web_site, https, server_entity, result.url.is_https())
            wsla.delete_instance()
        print(f"END UNRESOLVED WEB SITES LANDING RESOLUTION")

    def do_complete_unresolved_web_sites_scripts_withdraw(self, swas: List[ScriptWithdrawAssociation]) -> None:
        if len(swas) == 0:
            return
        print(f"\n\nSTART UNRESOLVED WEB SITES SCRIPTS WITHDRAW RESOLUTION")
        for i, swa in enumerate(swas):
            is_https = bool(swa.https)
            url = Url(swa.web_site)
            if is_https:
                scheme_url = url.https()
            else:
                scheme_url = url.http()
            print(f"association[{i+1}/{len(swas)}]: {scheme_url}")
            try:
                scripts = self.resolvers_wrapper.script_resolver.search_script_application_dependencies(scheme_url)
            except selenium.common.exceptions.WebDriverException:
                print(f"--> Can't resolve scripts...")
                continue
            for script in scripts:
                url_script = Url(script.src)
                scheme_url_script = SchemeUrl(script.src)
                se = helper_script.insert(script.src)
                helper_script_withdraw.insert(swa.web_site, se, scheme_url_script.is_https(), script.integrity)
                # completing script site - server
                script_site_entity = helper_script_site.insert(url_script)
                helper_script_site_lands.insert(script_site_entity, True, None, None)
                helper_script_site_lands.insert(script_site_entity, False, None, None)
                # TODO: manca effettivo landing
            swa.delete_instance()
        print(f"END UNRESOLVED WEB SITES SCRIPTS WITHDRAW RESOLUTION")

    def do_complete_unresolved_script_sites_landing(self, sslas: List[ScriptSiteLandsAssociation]) -> None:
        if len(sslas) == 0:
            return
        print(f"\n\nSTART UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
        for i, ssla in enumerate(sslas):
            site = Url(ssla.script_site)
            https = bool(ssla.starting_https)
            print(f"association[{i+1}/{len(sslas)}]: scheme={https}, url={site}")
            try:
                result = self.resolvers_wrapper.landing_resolver.do_single_request(site, https)
            except Exception:
                print(f"--> Can't resolve landing...")
                continue
            print(f"--> Landed on: {result.url}")
            server_entity = helper_script_server.insert(result.server)
            helper_script_site_lands.insert(ssla.script_site, https, server_entity, result.url.is_https())
            ssla.delete_instance()
        print(f"END UNRESOLVED SCRIPT SITES LANDING RESOLUTION")

    def do_complete_unresolved_mail_domain(self, mdcas: List[MailDomainComposedAssociation]) -> None:
        if len(mdcas) == 0:
            return
        print(f"\n\nSTART UNRESOLVED MAIL DOMAIN RESOLUTION")
        for i, mdca in enumerate(mdcas):
            mail_domain = DomainName(mdca.mail_domain.name.string)
            print(f"association[{i+1}/{len(mdcas)}]: {mail_domain}")
            try:
                result = self.resolvers_wrapper.dns_resolver.resolve_mail_domain(mail_domain)
                print(f"--> Resolved in: {result.mail_domain_path.stamp()}")
            except (DomainNonExistentError, NoAnswerError, UnknownReasonError):
                print(f"--> Can't resolve...")
                continue
            cname_dnes, mde, mses = helper_paths.insert_mx_path(result.mail_domain_path)
            for mail_server in result.mail_servers_paths.keys():
                helper_paths.insert_a_path_for_mail_servers(result.mail_servers_paths[mail_server], mde)
            mdca.delete_instance()
        print(f"END UNRESOLVED MAIL DOMAIN RESOLUTION")


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

