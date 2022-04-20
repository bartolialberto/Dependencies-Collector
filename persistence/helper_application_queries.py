from typing import Tuple, Set, Optional, List
from peewee import DoesNotExist
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_zone, helper_name_server, helper_domain_name, helper_ip_network, \
    helper_autonomous_system, helper_web_site, helper_web_server, helper_mail_domain, helper_mail_server, \
    helper_direct_zone
from persistence.BaseModel import db, ZoneEntity, IpAddressEntity, IpNetworkEntity, AutonomousSystemEntity, \
    WebSiteEntity, MailDomainEntity, WebServerEntity, MailServerEntity, NameServerEntity


def do_query_1() -> List[Tuple[ZoneEntity, Optional[Set[IpAddressEntity]], Optional[Set[IpNetworkEntity]], Optional[Set[AutonomousSystemEntity]]]]:
    zes = helper_zone.get_everyone()
    # this flag tells if we have to export a zone name that we know it is a zone (NS RR was resolved) but each
    # nameserver's A RR was not resolved. In that case the zone row will be added and for each field regarding the
    # relative infos will present the string value: ND
    only_complete_zones = False
    # QUERY
    print(f"Parameters: {len(zes)} zones retrieved from database.")
    count_complete_zones = 0
    count_incomplete_zones = 0
    result = list()
    with db.atomic():
        for ze in zes:
            try:
                nses = helper_name_server.get_zone_nameservers(ze)
            except NoDisposableRowsError:
                continue
            ases = set()
            iaes = set()
            ines = set()
            is_unresolved = False
            for nse in nses:
                try:
                    cname_dnes, dne_iaes = helper_domain_name.resolve_a_path(nse.name, as_persistence_entities=True)
                    # a_path = helper_domain_name.resolve_a_path(nse.name, as_persistence_entities=False)
                except (DoesNotExist, NoAvailablePathError):
                    is_unresolved = True
                    break
                for iae in dne_iaes:
                    iaes.add(iae)
                    try:
                        ine = helper_ip_network.get_of(iae)
                    except (DoesNotExist, NoAvailablePathError):
                        raise
                    ines.add(ine)
                    try:
                        ase = helper_autonomous_system.get_of_ip_address(iae)
                    except DoesNotExist:
                        print('')
                        continue  # TODO
                    ases.add(ase)
            if not only_complete_zones and is_unresolved:
                result.append((ze, None, None, None))       # TODO
                count_incomplete_zones = count_incomplete_zones + 1
            else:
                result.append((ze, iaes, ines, ases))
                count_complete_zones = count_complete_zones + 1
            if len(ases) > len(ines):
                print(f"ERROR: {ze.name} has more ases {len(ases)} than ines {len(ines)}")
    if not only_complete_zones:
        print(f"---> {count_complete_zones} complete zones.")
        print(f"---> {count_incomplete_zones} incomplete zones.")
    return result


def do_query_2() -> List[Tuple[WebSiteEntity, ZoneEntity]]:
    web_site_entities = helper_web_site.get_everyone()
    # QUERY
    print(f"Parameters: {len(web_site_entities)} web sites retrieved from database.")
    result = list()
    with db.atomic():
        for web_site_entity in web_site_entities:
            #
            https_web_server_entity, http_web_server_entity = helper_web_server.get_from(web_site_entity)
            try:
                web_site_domain_name_entity = helper_domain_name.get_of(web_site_entity)
            except DoesNotExist:
                raise
            #
            direct_zones_of_web_site = set()
            if https_web_server_entity is None:
                pass
            else:
                try:
                    ze = helper_zone.get_direct_zone_of(https_web_server_entity.name)
                    if ze is None:
                        pass
                    else:
                        direct_zones_of_web_site.add(ze)
                except DoesNotExist:
                    raise
            if http_web_server_entity != https_web_server_entity:
                if http_web_server_entity is None:
                    pass
                else:
                    try:
                        ze = helper_zone.get_direct_zone_of(http_web_server_entity.name)
                        if ze is None:
                            pass
                        else:
                            direct_zones_of_web_site.add(ze)
                    except DoesNotExist:
                        raise
            try:
                ze = helper_zone.get_direct_zone_of(web_site_domain_name_entity)
                direct_zones_of_web_site.add(ze)
            except DoesNotExist:
                pass          # could be a TLD that are not considered
            for ze in direct_zones_of_web_site:
                result.append((web_site_entity, ze))
    return result


def do_query_3() -> List[Tuple[MailDomainEntity, ZoneEntity]]:
    mail_domain_entities = helper_mail_domain.get_everyone()
    print(f"Parameters: {len(mail_domain_entities)} mail domains retrieved from database.")
    result = list()
    with db.atomic():
        for mail_domain_entity in mail_domain_entities:
            #
            try:
                mail_server_entities_of_mail_domain = helper_mail_server.get_every_of(mail_domain_entity)
            except DoesNotExist:
                continue
            #
            direct_zones_of_mail_domain = set()
            try:
                ze = helper_zone.get_direct_zone_of(mail_domain_entity.name)
                if ze is None:
                    pass
                else:
                    direct_zones_of_mail_domain.add(ze)
            except DoesNotExist:
                raise
            for mail_server_entity in mail_server_entities_of_mail_domain:
                try:
                    ze = helper_zone.get_direct_zone_of(mail_server_entity.name)
                    if ze is None:
                        pass
                    else:
                        direct_zones_of_mail_domain.add(ze)
                except DoesNotExist:
                    raise
            for ze in direct_zones_of_mail_domain:
                result.append((mail_domain_entity, ze))
    return result


def do_query_4() -> List[Tuple[WebSiteEntity, ZoneEntity]]:
    web_site_entities = helper_web_site.get_everyone()
    print(f"Parameters: {len(web_site_entities)} web sites retrieved from database.")
    result = list()
    with db.atomic():
        for web_site_entity in web_site_entities:
            #
            https_web_server_entity, http_web_server_entity = helper_web_server.get_from(web_site_entity)
            try:
                web_site_domain_name_entity = helper_domain_name.get_of(web_site_entity)
            except DoesNotExist:
                raise
            #
            zone_dependencies_of_web_site = set()
            if https_web_server_entity is None:
                pass
            else:
                try:
                    zes = helper_zone.get_zone_dependencies_of_entity_domain_name(https_web_server_entity.name)
                    for ze in zes:
                        zone_dependencies_of_web_site.add(ze)
                except DoesNotExist:
                    pass
            if http_web_server_entity != https_web_server_entity:
                if http_web_server_entity is None:
                    pass
                else:
                    try:
                        zes = helper_zone.get_zone_dependencies_of_entity_domain_name(http_web_server_entity.name)
                        for ze in zes:
                            zone_dependencies_of_web_site.add(ze)
                    except DoesNotExist:
                        pass
            try:
                zes = helper_zone.get_zone_dependencies_of_entity_domain_name(web_site_domain_name_entity)
                for ze in zes:
                    zone_dependencies_of_web_site.add(ze)
            except DoesNotExist:
                pass
            for ze in zone_dependencies_of_web_site:
                result.append((web_site_entity, ze))
    return result


def do_query_5() -> List[Tuple[MailDomainEntity, ZoneEntity]]:
    mail_domain_entities = helper_mail_domain.get_everyone()
    print(f"Parameters: {len(mail_domain_entities)} mail domains retrieved from database.")
    result = list()
    with db.atomic():
        for mail_domain_entity in mail_domain_entities:
            #
            try:
                mail_server_entities_of_mail_domain = helper_mail_server.get_every_of(mail_domain_entity)
            except DoesNotExist:
                continue
            #
            zone_dependencies_of_web_site = set()
            try:
                zes = helper_zone.get_zone_dependencies_of_entity_domain_name(mail_domain_entity.name)
                for ze in zes:
                    zone_dependencies_of_web_site.add(ze)
            except DoesNotExist:
                pass
            for mail_server_entity in mail_server_entities_of_mail_domain:
                try:
                    zes = helper_zone.get_zone_dependencies_of_entity_domain_name(mail_server_entity.name)
                    for ze in zes:
                        zone_dependencies_of_web_site.add(ze)
                except DoesNotExist:
                    pass
            for ze in zone_dependencies_of_web_site:
                result.append((mail_domain_entity, ze))
    return result


def do_query_6() -> List[Tuple[MailDomainEntity, Set[IpAddressEntity], Set[IpNetworkEntity], Set[AutonomousSystemEntity]]]:
    mail_domain_entities = helper_mail_domain.get_everyone()
    only_complete_mail_domain = False
    print(f"Parameters: {len(mail_domain_entities)} mail domains retrieved from database.")
    result = list()
    with db.atomic():
        for mail_domain_entity in mail_domain_entities:
            #
            try:
                mail_server_entities_of_mail_domain = helper_mail_server.get_every_of(mail_domain_entity)
            except DoesNotExist:
                continue
            #
            ip_addresses_of_mail_domain = set()
            ip_networks_of_mail_domain = set()
            autonomous_systems_of_mail_domain = set()
            for mail_server_entity in mail_server_entities_of_mail_domain:
                try:
                    cname_chain, iaes = helper_domain_name.resolve_a_path(mail_server_entity.name, as_persistence_entities=True)
                except NoAvailablePathError:
                    continue
                for iae in iaes:
                    ip_addresses_of_mail_domain.add(iae)
                    try:
                        ine = helper_ip_network.get_of(iae)
                    except DoesNotExist:
                        raise
                    ip_networks_of_mail_domain.add(ine)
                    try:
                        ase = helper_autonomous_system.get_of_ip_address(iae)
                    except DoesNotExist:
                        continue
                    autonomous_systems_of_mail_domain.add(ase)
            result.append((mail_domain_entity, ip_addresses_of_mail_domain, ip_networks_of_mail_domain, autonomous_systems_of_mail_domain))
    return result


def do_query_7() -> List[Tuple[WebServerEntity, Set[IpAddressEntity], Set[IpNetworkEntity], Set[AutonomousSystemEntity]]]:
    web_server_entities = helper_web_server.get_everyone()
    print(f"Parameters: {len(web_server_entities)} web servers retrieved from database.")
    result = list()
    with db.atomic():
        for web_server_entity in web_server_entities:
            ip_addresses_of_web_server = set()
            ip_networks_of_web_server = set()
            autonomous_systems_of_web_server = set()
            try:
                cname_chain, iaes = helper_domain_name.resolve_a_path(web_server_entity.name, as_persistence_entities=True)
            except NoAvailablePathError:
                continue
            for iae in iaes:
                ip_addresses_of_web_server.add(iae)
                try:
                    ine = helper_ip_network.get_of(iae)
                except DoesNotExist:
                    raise
                ip_networks_of_web_server.add(ine)
                try:
                    ase = helper_autonomous_system.get_of_ip_address(iae)
                except DoesNotExist:
                    continue
                autonomous_systems_of_web_server.add(ase)
            result.append((web_server_entity, ip_addresses_of_web_server, ip_networks_of_web_server, autonomous_systems_of_web_server))
    return result


#TODO
def do_query_8() -> List[Tuple[IpNetworkEntity, AutonomousSystemEntity, Set[WebServerEntity], Set[MailServerEntity], Set[NameServerEntity], Set[ZoneEntity], Set[WebSiteEntity], Set[MailDomainEntity]]]:
    network_entities = helper_ip_network.get_everyone()
    print(f"Parameters: {len(network_entities)} IP networks retrieved from database.")
    result = list()
    with db.atomic():
        for network_entity in network_entities:
            try:
                autonomous_system = helper_autonomous_system.get_of_entity_ip_network(network_entity)
            except DoesNotExist:
                print(f"{network_entity.compressed_notation} does not exist..")
                continue
            try:
                dnes = helper_domain_name.get_everyone_from_ip_network(network_entity)
            except NoDisposableRowsError:
                raise
            try:
                belonging_webservers = helper_web_server.filter_domain_names(dnes)
            except NoDisposableRowsError:
                belonging_webservers = set()
            try:
                belonging_mailservers = helper_mail_server.filter_domain_names(dnes)
            except NoDisposableRowsError:
                belonging_mailservers = set()
            try:
                belonging_nameservers = helper_name_server.filter_domain_names(dnes)
            except NoDisposableRowsError:
                belonging_nameservers = set()
            try:
                zones_entirely_contained = helper_zone.get_entire_zones_from_nameservers_pool(belonging_nameservers)
            except NoDisposableRowsError:
                zones_entirely_contained = set()
            try:
                direct_zones = helper_direct_zone.get_from_zone_dataset(zones_entirely_contained)
            except NoDisposableRowsError:
                direct_zones = set()
            website_directzones_entirely_contained = set()
            maildomain_directzones_entirely_contained = set()
            # TODO



            result.append((
                network_entity,
                autonomous_system,
                belonging_webservers,
                belonging_mailservers,
                belonging_nameservers,
                zones_entirely_contained,
                website_directzones_entirely_contained,
                maildomain_directzones_entirely_contained
            ))
    return result
