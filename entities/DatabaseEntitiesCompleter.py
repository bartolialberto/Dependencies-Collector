import ipaddress
from datetime import datetime
from typing import List, Set, Tuple, Union
import selenium
from entities.ApplicationResolversWrapper import ApplicationResolversWrapper
from entities.DomainName import DomainName
from entities.Url import Url
from entities.EntryIpAsDatabase import EntryIpAsDatabase
from entities.resolvers.results.ASResolverResultForROVPageScraping import ASResolverResultForROVPageScraping
from entities.resolvers.results.AutonomousSystemResolutionResults import AutonomousSystemResolutionResults
from exceptions.AutonomousSystemNotFoundError import AutonomousSystemNotFoundError
from exceptions.DomainNonExistentError import DomainNonExistentError
from exceptions.EmptyInputNoElaborationNeededError import EmptyInputNoElaborationNeededError
from exceptions.NetworkNotFoundError import NetworkNotFoundError
from exceptions.NoAnswerError import NoAnswerError
from exceptions.NotROVStateTypeError import NotROVStateTypeError
from exceptions.TableEmptyError import TableEmptyError
from exceptions.TableNotPresentError import TableNotPresentError
from exceptions.UnknownReasonError import UnknownReasonError
from persistence import helper_autonomous_system, helper_ip_range_tsv, helper_ip_range_rov, helper_web_server, \
    helper_web_site_lands, helper_script_server, helper_script_site_lands, helper_script_withdraw, helper_script, \
    helper_script_site, helper_paths, helper_network_numbers, helper_rov, helper_prefixes_table, helper_script_hosted_on
from persistence.BaseModel import IpAddressDependsAssociation, WebSiteLandsAssociation, ScriptWithdrawAssociation, \
    ScriptSiteLandsAssociation, MailDomainComposedAssociation, AccessAssociation, db
from utils import datetime_utils, string_utils


class DatabaseEntitiesCompleter:
    """
    This class represents the tool which concern is to recover all unresolved entities from database used as input.
    It needs all the resolvers of the application, so the only attribute is an instance of the
    ApplicationResolversWrapper class.

    ...

    Attributes
    ----------
    resolvers_wrapper : ApplicationResolversWrapper
        An in stance of the wrapper of all application resolvers.
    """
    def __init__(self, resolvers_wrapper: ApplicationResolversWrapper):
        """
        Instantiate the object.

        :param resolvers_wrapper: The wrapper of all the application resolvers.
        :type resolvers_wrapper: ApplicationResolversWrapper
        """
        self.resolvers_wrapper = resolvers_wrapper

    def do_complete_unresolved_entities(self, unresolved_entities: Set[Union[WebSiteLandsAssociation, ScriptWithdrawAssociation, ScriptSiteLandsAssociation, AccessAssociation, MailDomainComposedAssociation, IpAddressDependsAssociation]]) -> Set[DomainName]:
        """
        This method is actually the one that executes (tries to execute) the completion of all unresolved entities.
        It also deals with the insertion in the database if there's new data resolved.

        :param unresolved_entities: All the unresolved entities.
        :type unresolved_entities: Set[Union[WebSiteLandsAssociation, ScriptWithdrawAssociation, ScriptSiteLandsAssociation, AccessAssociation, MailDomainComposedAssociation, IpAddressDependsAssociation]]
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
        total_new_resolution = 0
        new_domain_names = set()
        try:
            wslas_resolved, new_dnes = self.do_complete_unresolved_web_sites_landing(wslas)
            total_new_resolution = total_new_resolution + wslas_resolved
            new_domain_names = new_domain_names.union(new_dnes)
            print(f"RESOLVED {wslas_resolved}/{len(wslas)} associations.")
        except EmptyInputNoElaborationNeededError:
            pass

        try:
            aas_resolved = self.do_complete_domain_names_with_no_access(aas)
            total_new_resolution = total_new_resolution + aas_resolved
            print(f"RESOLVED {aas_resolved}/{len(aas)} associations.")
        except EmptyInputNoElaborationNeededError:
            pass

        try:
            swas_resolved = self.do_complete_unresolved_web_sites_scripts_withdraw(swas)
            total_new_resolution = total_new_resolution + swas_resolved
            print(f"RESOLVED {swas_resolved}/{len(swas)} associations.")
        except EmptyInputNoElaborationNeededError:
            pass

        try:
            sslas_resolved, new_dnes = self.do_complete_unresolved_script_sites_landing(sslas)
            total_new_resolution = total_new_resolution + sslas_resolved
            new_domain_names = new_domain_names.union(new_dnes)
            print(f"RESOLVED {sslas_resolved}/{len(sslas)} associations.")
        except EmptyInputNoElaborationNeededError:
            pass

        try:
            mdcas_resolved, new_dnes = self.do_complete_unresolved_mail_domain(mdcas)
            total_new_resolution = total_new_resolution + mdcas_resolved
            new_domain_names = new_domain_names.union(new_dnes)
            print(f"RESOLVED {mdcas_resolved}/{len(mdcas)} associations.")
        except EmptyInputNoElaborationNeededError:
            pass

        try:
            iadas_resolved = self.do_complete_unresolved_ip_address_depends_association(iadas)
            total_new_resolution = total_new_resolution + iadas_resolved
            print(f"RESOLVED {iadas_resolved}/{len(iadas)} associations.")
        except EmptyInputNoElaborationNeededError:
            pass
        print(f"Total database completion execution time is: {datetime_utils.compute_delta_and_stamp(start_time)}")
        print(f"Total new entities resolved: {total_new_resolution}/{len(unresolved_entities)}")
        print("********** END DATABASE COMPLETION ELABORATION **********\n")
        return new_domain_names

    def do_complete_domain_names_with_no_access(self, aas: List[AccessAssociation]) -> int:
        """
        Method that tries to complete unresolved AccessAssociation entities.

        :param aas: List of AccessAssociation entities.
        :type aas: List[AccessAssociation]
        """
        if len(aas) == 0:
            raise EmptyInputNoElaborationNeededError
        print(f"\nSTART DOMAIN NAME WITH NO ACCESS RESOLVING")
        resolved = 0
        with db.atomic():
            for i, aa in enumerate(aas):
                domain_name = DomainName(aa.domain_name.string)
                print(f"association[{i+1}/{len(aas)}]: ", end='')
                try:
                    a_path = self.resolvers_wrapper.dns_resolver.resolve_a_path(domain_name)
                except (NoAnswerError, DomainNonExistentError, UnknownReasonError):
                    print(f"{domain_name} not resolved...")
                    continue
                print(f"{a_path.stamp()}")
                helper_paths.insert_a_path(a_path)
                aa.delete_instance()
                resolved = resolved + 1
        print(f"END DOMAIN NAME WITH NO ACCESS RESOLVING")
        return resolved

    def do_complete_unresolved_web_sites_landing(self, wslas: List[WebSiteLandsAssociation]) -> Tuple[int, Set[DomainName]]:
        """
        Method that tries to complete unresolved WebSiteLandsAssociation entities.

        :param wslas: List of WebSiteLandsAssociation entities.
        :type wslas: List[WebSiteLandsAssociation]
        """
        if len(wslas) == 0:
            raise EmptyInputNoElaborationNeededError
        print(f"\n\nSTART UNRESOLVED WEB SITES LANDING RESOLUTION")
        resolved = 0
        new_dnes = set()
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
                new_dnes.add(result.server)
                helper_web_site_lands.upsert(wsla.web_site, https, result.url, server_entity)
                wsla.delete_instance()
                resolved = resolved + 1
        print(f"END UNRESOLVED WEB SITES LANDING RESOLUTION")
        return resolved, new_dnes

    def do_complete_unresolved_web_sites_scripts_withdraw(self, swas: List[ScriptWithdrawAssociation]) -> int:
        """
        Method that tries to complete unresolved ScriptWithdrawAssociation entities.

        :param swas: List of ScriptWithdrawAssociation entities.
        :type swas: List[ScriptWithdrawAssociation]
        """
        if len(swas) == 0:
            raise EmptyInputNoElaborationNeededError
        if not self.resolvers_wrapper.execute_script_resolving:
            print(f"\n> execute_script_resolving is set to False. If you want to perform completion of script dependencies switch the execute_script_resolving flag to True in the next execution..")
            raise EmptyInputNoElaborationNeededError
        print(f"\n\nSTART UNRESOLVED WEB SITES SCRIPTS WITHDRAW RESOLUTION")
        resolved = 0
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
                    # TODO: manca effettivo landing
                swa.delete_instance()
                resolved = resolved + 1
        print(f"END UNRESOLVED WEB SITES SCRIPTS WITHDRAW RESOLUTION")
        return resolved

    def do_complete_unresolved_script_sites_landing(self, sslas: List[ScriptSiteLandsAssociation]) -> Tuple[int, Set[DomainName]]:
        """
        Method that tries to complete unresolved ScriptSiteLandsAssociation entities.

        :param sslas: List of ScriptSiteLandsAssociation entities.
        :type sslas: List[ScriptSiteLandsAssociation]
        """
        if len(sslas) == 0:
            raise EmptyInputNoElaborationNeededError
        print(f"\nSTART UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
        resolved = 0
        new_dnes = set()
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
                new_dnes.add(result.server)
                helper_script_site_lands.upsert(ssla.script_site, ssla.starting_https, result.url, server_entity)
                ssla.delete_instance()
                resolved = resolved + 1
        print(f"END UNRESOLVED SCRIPT SITES LANDING RESOLUTION")
        return resolved, new_dnes

    def do_complete_unresolved_mail_domain(self, mdcas: List[MailDomainComposedAssociation]) -> Tuple[int, Set[DomainName]]:
        """
        Method that tries to complete unresolved MailDomainComposedAssociation entities.

        :param mdcas: List of MailDomainComposedAssociation entities.
        :type mdcas: List[MailDomainComposedAssociation]
        """
        if len(mdcas) == 0:
            raise EmptyInputNoElaborationNeededError
        print(f"\n\nSTART UNRESOLVED MAIL DOMAIN RESOLUTION")
        resolved = 0
        new_dnes = set()
        with db.atomic():
            for i, mdca in enumerate(mdcas):
                mail_domain = DomainName(mdca.mail_domain.name.string)
                print(f"association[{i+1}/{len(mdcas)}]: {mail_domain}")
                try:
                    result = self.resolvers_wrapper.dns_resolver.resolve_mail_domain(mail_domain)
                    print(f"association[{i + 1}/{len(mdcas)}]: {result.mail_domain_path}")
                    for j, mail_server in enumerate(result.mail_servers_paths.keys()):
                        new_dnes.add(mail_server)
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
                resolved = resolved + 1
        print(f"END UNRESOLVED MAIL DOMAIN RESOLUTION")
        return resolved, new_dnes

    def do_complete_unresolved_ip_address_depends_association(self, iadas: List[IpAddressDependsAssociation]) -> int:
        """
        Method that tries to complete unresolved IpAddressDependsAssociation entities.

        :param iadas: List of IpAddressDependsAssociation entities.
        :type iadas: List[IpAddressDependsAssociation]
        """
        if len(iadas) == 0:
            raise EmptyInputNoElaborationNeededError
        if not self.resolvers_wrapper.execute_rov_scraping:
            print(f"\n> execute_rov_scraping is set to False. If you want to perform completion of ROV entities switch the execute_rov_scraping flag to True in the next execution..")
            raise EmptyInputNoElaborationNeededError
        print(f"\n\nSTART UNRESOLVED IP ADDRESS DEPENDENCIES RESOLUTION")
        resolved = 0
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
                    resolved = resolved + 1
            print(f"END UNRESOLVED IP ADDRESS DEPENDENCIES RESOLUTION")
            return resolved

    def __do_tsv_database_resolving__(self, ip_address: ipaddress.IPv4Address) -> Tuple[EntryIpAsDatabase, ipaddress.IPv4Network]:
        """
        Method that performs the .tsv database resolving in a 'compact' way, without any prints and handling all
        possible exceptions in the same way.

        :param ip_address: An IP address.
        :type ip_address: ipaddress.IPv4Address
        :raise ValueError: If the binary search auxiliary method raises a ValueError exception. In particular it is
        impossible to instantiate a valid Ipv4Address from an entry of the .tsv database.
        If the matched entry is formatted wrongly, not as described in https://iptoasn.com/.
        In particular one of 3 errors occurred:
            - the start_ip_range is not a valid ip address
            - the end_ip_range is not a valid ip address
            - the as_number is not a valid integer number
        If last is not greater than first or if first address version is not 4 or 6.
        If there's not a network in which is contained the ip address parameter.
        :raise AutonomousSystemNotFoundError: If there is no Autonomous System that match the ip parameter.
        :return: Tuple of the .tsb database entry and the network that the IP address belongs to.
        :rtype: Tuple[EntryIpAsDatabase, ipaddress.IPv4Network]
        """
        try:
            entry = self.resolvers_wrapper.ip_as_database.resolve_range(ip_address)
            net, all_net = entry.get_network_of_ip(ip_address)
        except (ValueError, AutonomousSystemNotFoundError):
            raise
        return entry, net
