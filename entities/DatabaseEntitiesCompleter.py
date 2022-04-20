import ipaddress
from datetime import datetime
from typing import List, Set, Tuple
import selenium
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.DomainName import DomainName
from entities.Url import Url
from entities.EntryIpAsDatabase import EntryIpAsDatabase
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from entities.resolvers.results.AutonomousSystemResolutionResults import AutonomousSystemResolutionResults
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError
from exceptions.UnknownReasonError import UnknownReasonError
from persistence import helper_autonomous_system, helper_ip_range_tsv, helper_ip_range_rov, helper_web_server, \
    helper_web_site_lands, helper_script_server, helper_script_site_lands, helper_script_withdraw, helper_script, \
    helper_script_site, helper_paths, helper_network_numbers, helper_rov, helper_prefixes_table, helper_script_hosted_on
from persistence.BaseModel import IpAddressDependsAssociation, WebSiteLandsAssociation, ScriptWithdrawAssociation,\
    ScriptSiteLandsAssociation, MailDomainComposedAssociation, AccessAssociation, db
from utils import datetime_utils, string_utils


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
    def __init__(self, resolvers_wrapper: ApplicationResolversWrapper):
        """
        Instantiate the object.

        :param resolvers_wrapper: The wrapper of all the application resolvers.
        :type resolvers_wrapper: ApplicationResolversWrapper
        """
        self.resolvers_wrapper = resolvers_wrapper

    def do_complete_unresolved_entities(self, unresolved_entities: set) -> None:
        """
        This method is actually the one that executes (tries to execute) the completion of all unresolved entities.
        It also deals with the insertion in the database if there's new data resolved.

        :param unresolved_entities: All the unresolved entities.
        :type unresolved_entities: Set[UnresolvedEntityWrapper]
        """
        start_time = datetime.now()
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
            elif isinstance(unresolved_entity, MailDomainComposedAssociation):
                mdcas.append(unresolved_entity)
            elif isinstance(unresolved_entity, IpAddressDependsAssociation):
                iadas.append(unresolved_entity)
            else:
                raise ValueError
        print("\n********** START DATABASE COMPLETION ELABORATION **********")
        self.do_complete_unresolved_web_sites_landing(wslas)
        self.do_complete_domain_names_with_no_access(aas)
        self.do_complete_unresolved_web_sites_scripts_withdraw(swas)
        self.do_complete_unresolved_script_sites_landing(sslas)
        self.do_complete_unresolved_mail_domain(mdcas)
        self.do_complete_unresolved_ip_address_depends_association(iadas)
        print(f"Total database completion execution time is: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print("********** END DATABASE COMPLETION ELABORATION **********\n")

    def do_complete_domain_names_with_no_access(self, aas: List[AccessAssociation]) -> None:
        if len(aas) == 0:
            return
        print(f"\nSTART DOMAIN NAME WITH NO ACCESS RESOLVING")
        with db.atomic():
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
        with db.atomic():
            for i, wsla in enumerate(wslas):
                site = Url(wsla.web_site.url.string)
                https = bool(wsla.starting_https)
                print(f"association[{i+1}/{len(wslas)}]: scheme={https}, url={site}")
                try:
                    result = self.resolvers_wrapper.landing_resolver.do_single_request(site, https)
                except Exception:
                    print(f"--> Can't resolve landing...")
                    continue
                print(f"--> Landed on: {result.url}")
                server_entity = helper_web_server.insert(result.server)
                helper_web_site_lands.insert(wsla.web_site, https, result.url, server_entity)
                wsla.delete_instance()
        print(f"END UNRESOLVED WEB SITES LANDING RESOLUTION")

    def do_complete_unresolved_web_sites_scripts_withdraw(self, swas: List[ScriptWithdrawAssociation]) -> None:
        if len(swas) == 0:
            return
        if not self.resolvers_wrapper.execute_script_resolving:
            print(f"\n> execute_script_resolving is set to False. If you want to perform completion of script dependencies switch the execute_script_resolving flag to True in the next execution..")
            return
        print(f"\n\nSTART UNRESOLVED WEB SITES SCRIPTS WITHDRAW RESOLUTION")
        with db.atomic():
            for i, swa in enumerate(swas):
                url = Url(swa.web_site.url.string)
                if swa.https:
                    scheme_url = url.https()
                else:
                    scheme_url = url.http()
                print(f"association[{i+1}/{len(swas)}]: {scheme_url}")
                try:
                    scripts = self.resolvers_wrapper.script_resolver.search_script_application_dependencies(scheme_url)
                except selenium.common.exceptions.WebDriverException:
                    print(f"--> Can't resolve scripts...")
                    continue
                if len(scripts) == 0:
                    print(f"--> Url doesn't provide main frame scripts")
                for j, script in enumerate(scripts):
                    url_script = Url(script.src)
                    se = helper_script.insert(script.src)
                    helper_script_withdraw.insert(swa.web_site, se, swa.https, script.integrity)
                    # completing script site - server
                    script_site_entity = helper_script_site.insert(url_script)
                    helper_script_hosted_on.insert(se, script_site_entity)
                    helper_script_site_lands.insert(script_site_entity, True, None, None)
                    helper_script_site_lands.insert(script_site_entity, False, None, None)
                    print(f"--> script[{j+1}/{len(scripts)}]: integrity={script.integrity}, src={script.src}")
                    # TODO: manca effettivo landing che viene fatto successivamente
                swa.delete_instance()
        print(f"END UNRESOLVED WEB SITES SCRIPTS WITHDRAW RESOLUTION")

    def do_complete_unresolved_script_sites_landing(self, sslas: List[ScriptSiteLandsAssociation]) -> None:
        if len(sslas) == 0:
            return
        print(f"\nSTART UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
        with db.atomic():
            for i, ssla in enumerate(sslas):
                site = Url(ssla.script_site.url.string)
                print(f"association[{i+1}/{len(sslas)}]: scheme={string_utils.stamp_https_from_bool(ssla.starting_https)}, url={site}")
                try:
                    result = self.resolvers_wrapper.landing_resolver.do_single_request(site, ssla.starting_https)
                except Exception:
                    print(f"--> Can't resolve landing...")
                    continue
                print(f"--> Landed on: {result.url}")
                server_entity = helper_script_server.insert(result.server)
                helper_script_site_lands.insert(ssla.script_site, ssla.starting_https, result.url, server_entity)
                ssla.delete_instance()
        print(f"END UNRESOLVED SCRIPT SITES LANDING RESOLUTION")

    def do_complete_unresolved_mail_domain(self, mdcas: List[MailDomainComposedAssociation]) -> None:
        if len(mdcas) == 0:
            return
        print(f"\n\nSTART UNRESOLVED MAIL DOMAIN RESOLUTION")
        with db.atomic():
            for i, mdca in enumerate(mdcas):
                mail_domain = DomainName(mdca.mail_domain.name.string)
                print(f"association[{i+1}/{len(mdcas)}]: {mail_domain}")
                try:
                    result = self.resolvers_wrapper.dns_resolver.resolve_mail_domain(mail_domain)
                    print(f"association[{i + 1}/{len(mdcas)}]: {result.mail_domain_path}")
                    for j, mail_server in enumerate(result.mail_servers_paths.keys()):
                        if result.mail_servers_paths[mail_server] is not None:
                            print(f"--> mail server[{j+1}/{len(result.mail_servers_paths.keys())}] {result.mail_servers_paths[mail_server].stamp()}")
                        else:
                            print(f"--> mail server[{j+1}/{len(result.mail_servers_paths.keys())}] {mail_server} unresolved..")
                except (DomainNonExistentError, NoAnswerError, UnknownReasonError):
                    # print(f"--> Can't resolve...")
                    continue
                cname_dnes, mde, mses = helper_paths.insert_mx_path(result.mail_domain_path)
                for mail_server in result.mail_servers_paths.keys():
                    if result.mail_servers_paths[mail_server] is None:
                        pass
                    else:
                        helper_paths.insert_a_path_for_mail_servers(result.mail_servers_paths[mail_server], mde)
                mdca.delete_instance()
        print(f"END UNRESOLVED MAIL DOMAIN RESOLUTION")

    def do_complete_unresolved_ip_address_depends_association(self, iadas: List[IpAddressDependsAssociation]):
        if len(iadas) == 0:
            return
        if not self.resolvers_wrapper.execute_rov_scraping:
            print(f"\n> execute_rov_scraping is set to False. If you want to perform completion of ROV entities switch the execute_rov_scraping flag to True in the next execution..")
            return
        print(f"\n\nSTART UNRESOLVED IP ADDRESS DEPENDENCIES RESOLUTION")
        results = AutonomousSystemResolutionResults()
        ase_dict = dict()
        ip_address_depends_dict = dict()
        with db.atomic():
            for i, iada in enumerate(iadas):
                ip_address = ipaddress.IPv4Address(iada.ip_address.exploded_notation)
                entry = None
                ip_range_tsv = None
                ip_range_tsv_entity = iada.ip_range_tsv
                if ip_range_tsv_entity is None:
                    try:
                        entry, ip_range_tsv = self.__do_tsv_database_resolving__(ip_address)
                    except (ValueError, AutonomousSystemNotFoundError):
                        print(f"For {ip_address} no entry found in IP-AS database..")
                        continue
                    irte = helper_ip_range_tsv.insert(ip_range_tsv.compressed)
                    ase = helper_autonomous_system.insert(entry)
                    helper_network_numbers.insert(irte, ase)

                    iada.ip_range_tsv = irte

                    ase_dict[ase.number] = ase
                else:
                    ase = helper_autonomous_system.get_of_entity_ip_range_tsv(ip_range_tsv_entity)
                    try:
                        entries = self.resolvers_wrapper.ip_as_database.get_entries_from_as_number(ase.number)
                    except AutonomousSystemNotFoundError:
                        print(f"No entry found for AS{ase.number}...")
                        continue
                    for entry in entries:
                        try:
                            ip_range_tsv, networks = entry.get_network_of_ip(ip_address)
                            break
                        except ValueError:
                            pass
                    if ip_range_tsv is None:
                        print(f"For {ip_address} no IP range .tsv computed..")
                        continue
                    ase_dict[ase.number] = ase
                results.add_complete_result(ip_address, DomainName('PLACEHOLDER_'+str(i)), entry, ip_range_tsv)
                ip_address_depends_dict[ip_address] = iada
        with db.atomic():
            reformat = ASResolverResultForROVPageScraping(results)
            for i, as_number in enumerate(reformat.results.keys()):
                print(f"Loading page [{i + 1}/{len(reformat.results.keys())}] for AS{as_number}")
                try:
                    self.resolvers_wrapper.rov_page_scraper.load_as_page(as_number)
                except (selenium.common.exceptions.WebDriverException, TableNotPresentError, TableEmptyError,
                        NetworkNotFoundError, NotROVStateTypeError):
                    print(f"Can't load AS{as_number} page..")
                    continue
                for ip_address in reformat.results[as_number].keys():
                    try:
                        row = self.resolvers_wrapper.rov_page_scraper.get_network_if_present(ip_address)
                    except (selenium.common.exceptions.WebDriverException, TableNotPresentError, TableEmptyError, NetworkNotFoundError):
                        print(f"--> for {ip_address} no row found..")
                        continue
                    print(f"--> for {ip_address}: found row: {str(row)}")
                    irre = helper_ip_range_rov.insert(row.prefix)
                    re = helper_rov.insert(row)
                    ase = ase_dict[as_number]
                    helper_prefixes_table.insert(irre, re, ase)
                    q = IpAddressDependsAssociation\
                        .update(ip_range_tsv=ip_address_depends_dict[ip_address].ip_range_tsv, ip_range_rov=irre)\
                        .where(IpAddressDependsAssociation.ip_address == ip_address_depends_dict[ip_address].ip_address)
                    q.execute()
            print(f"END UNRESOLVED IP ADDRESS DEPENDENCIES RESOLUTION")

    def __do_tsv_database_resolving__(self, ip_address: ipaddress.IPv4Address) -> Tuple[EntryIpAsDatabase, ipaddress.IPv4Network]:
        try:
            entry = self.resolvers_wrapper.ip_as_database.resolve_range(ip_address)
            net, all_net = entry.get_network_of_ip(ip_address)
        except (ValueError, AutonomousSystemNotFoundError):
            raise
        return entry, net

