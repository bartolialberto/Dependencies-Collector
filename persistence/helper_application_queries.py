from typing import Tuple, Set, Optional, List
from peewee import DoesNotExist, chunked
from exceptions.NoAvailablePathError import NoAvailablePathError
from exceptions.NoDisposableRowsError import NoDisposableRowsError
from persistence import helper_zone, helper_name_server, helper_domain_name, helper_ip_network, \
    helper_autonomous_system, helper_web_site, helper_web_server, helper_mail_domain, helper_mail_server, \
    helper_direct_zone
from persistence.BaseModel import db, ZoneEntity, IpAddressEntity, IpNetworkEntity, AutonomousSystemEntity, \
    WebSiteEntity, MailDomainEntity, WebServerEntity, MailServerEntity, NameServerEntity


def do_query_1() -> List[Tuple[ZoneEntity, Optional[Set[IpAddressEntity]], Optional[Set[IpNetworkEntity]], Optional[Set[AutonomousSystemEntity]]]]:
    """
    This query computes data regarding the architecture of every single zone in the database.
    If some information regarding the zone architecture are missing then such zone is not considered in the results,
    because the resulting information of such zone are counterfeiters.
    Example: nameserver abc of zone xyz can't be resolved in any IP addresses, that means xyz will be not present in the
    final result.

    """
    zes = helper_zone.get_everyone()
    # QUERY
    print(f"Parameters: {len(zes)} zones retrieved from database.")
    count_complete_zones = 0
    count_incomplete_zones = 0
    result = list()
    for chunk in chunked(zes, 400):
        with db.atomic():       # peewee transaction
            for ze in chunk:
                try:
                    nses = helper_name_server.get_zone_nameservers(ze)
                except NoDisposableRowsError:
                    print(f"!!! unresolvable nameservers from zone: {ze.name} !!!")
                    continue
                ases = set()
                iaes = set()
                ines = set()
                is_unresolved = False
                for nse in nses:
                    try:
                        cname_dnes, dne_iaes = helper_domain_name.resolve_a_path(nse.name, as_persistence_entities=True)
                    except (DoesNotExist, NoAvailablePathError):
                        print(f"!!! unresolvable A path from name server {nse.name.string} of zone: {ze.name} !!!")
                        is_unresolved = True
                        break
                    for iae in dne_iaes:
                        iaes.add(iae)
                        try:
                            ine = helper_ip_network.get_of(iae)
                        except (DoesNotExist, NoAvailablePathError):
                            print(f"!!! unresolvable network from IP address {iae.exploded_notation} of nameserver {nse.name.string} belonging to zone: {ze.name} !!!")
                            raise
                        ines.add(ine)
                        try:
                            ase = helper_autonomous_system.get_of_ip_address(iae)
                        except DoesNotExist:
                            print(f"!!! unresolvable AS from IP address {iae.exploded_notation} of nameserver {nse.name.string} belonging to zone: {ze.name} !!!")
                            raise
                        ases.add(ase)
                if is_unresolved:
                    count_incomplete_zones = count_incomplete_zones + 1
                else:
                    result.append((ze, iaes, ines, ases))
                    count_complete_zones = count_complete_zones + 1
                if len(ases) > len(ines):
                    print(f"ERROR: {ze.name} has more ASes {len(ases)} than IP networks {len(ines)}")
    print(f"---> {count_complete_zones} complete zones. {count_incomplete_zones} incomplete zones.")
    return result


def do_query_2() -> List[Tuple[WebSiteEntity, ZoneEntity]]:
    """
    This query computes direct zones of every website in the database.
    Missing information regarding a website are simply ignored.
    Example: the HTTP server associated to a website xyz is NULL, the remaining dependencies regarding xyz will be
    written in the result.

    """
    web_site_entities = helper_web_site.get_everyone()
    # QUERY
    print(f"Parameters: {len(web_site_entities)} web sites retrieved from database.")
    result = list()
    for chunk in chunked(web_site_entities, 400):
        with db.atomic():       # peewee transaction
            for web_site_entity in chunk:
                # getting webservers and domain name associated to website
                try:
                    https_web_server_entity, http_web_server_entity = helper_web_server.get_from(web_site_entity)
                except NoDisposableRowsError:
                    print(f"!!! unresolvable webservers of website: {web_site_entity.url.string} !!!")
                    continue
                try:
                    web_site_domain_name_entity = helper_domain_name.get_of(web_site_entity)
                except DoesNotExist:
                    print(f"!!! unresolvable domain name associated to website: {web_site_entity.url.string} !!!")
                    raise
                # webservers direct zones
                direct_zones_of_web_site = set()
                if https_web_server_entity is None:
                    pass
                else:
                    try:
                        ze = helper_zone.get_direct_zone_of(https_web_server_entity.name)
                        if ze is None:
                            print(f"--> NULL direct zone of webserver {https_web_server_entity.name.string} associated to website: {web_site_entity.url.string}")
                            pass
                        else:
                            direct_zones_of_web_site.add(ze)
                    except DoesNotExist:
                        print(f"!!! unresolvable direct zone of webserver {https_web_server_entity.name.string} associated to website: {web_site_entity.url.string} !!!")
                        raise
                if http_web_server_entity != https_web_server_entity:
                    if http_web_server_entity is None:
                        pass
                    else:
                        try:
                            ze = helper_zone.get_direct_zone_of(http_web_server_entity.name)
                            if ze is None:
                                print(
                                    f"--> NULL direct zone of webserver {http_web_server_entity.name.string} associated to website: {web_site_entity.url.string}")
                                pass
                            else:
                                direct_zones_of_web_site.add(ze)
                        except DoesNotExist:
                            print(f"!!! unresolvable direct zone of webserver {https_web_server_entity.name.string} associated to website: {web_site_entity.url.string} !!!")
                            raise
                # website direct zone
                try:
                    ze = helper_zone.get_direct_zone_of(web_site_domain_name_entity)
                    if ze is None:
                        print(f"--> NULL direct zone of website: {web_site_entity.url.string}")
                        pass
                    else:
                        direct_zones_of_web_site.add(ze)
                except DoesNotExist:
                    print(f"!!! unresolvable direct zone of website: {web_site_entity.url.string} !!!")
                    pass          # could be a TLD that are not considered
                for ze in direct_zones_of_web_site:
                    result.append((web_site_entity, ze))
    return result


def do_query_3() -> List[Tuple[MailDomainEntity, ZoneEntity]]:
    """
    This query computes direct zones of every mail domain in the database.

    """
    mail_domain_entities = helper_mail_domain.get_everyone()
    print(f"Parameters: {len(mail_domain_entities)} mail domains retrieved from database.")
    result = list()
    for chunk in chunked(mail_domain_entities, 400):
        with db.atomic():       # peewee transaction
            for mail_domain_entity in chunk:
                # getting mail servers
                try:
                    mail_server_entities_of_mail_domain = helper_mail_server.get_every_of(mail_domain_entity)
                except DoesNotExist:
                    print(f"!!! unresolvable mailservers of maildomain: {mail_domain_entity.name.string} !!!")
                    continue
                direct_zones_of_mail_domain = set()
                # direct zone of mail domain
                try:
                    ze = helper_zone.get_direct_zone_of(mail_domain_entity.name)
                    if ze is None:
                        print(f"--> NULL direct zone of maildomain: {mail_domain_entity.name.string}")
                        pass
                    else:
                        direct_zones_of_mail_domain.add(ze)
                except DoesNotExist:
                    print(f"!!! unresolvable direct zone of maildomain: {mail_domain_entity.name.string} !!!")
                    raise
                # direct zones of mail servers
                for mail_server_entity in mail_server_entities_of_mail_domain:
                    try:
                        ze = helper_zone.get_direct_zone_of(mail_server_entity.name)
                        if ze is None:
                            print(f"--> NULL direct zone of mailserver {mail_server_entity.name.string} associated to maildomain: {mail_domain_entity.name.string}")
                            pass
                        else:
                            direct_zones_of_mail_domain.add(ze)
                    except DoesNotExist:
                        print(f"!!! unresolvable direct zone of mailserver {mail_server_entity.name.string} associated to maildomain: {mail_domain_entity.name.string} !!!")
                        raise
                for ze in direct_zones_of_mail_domain:
                    result.append((mail_domain_entity, ze))
    return result


def do_query_4() -> List[Tuple[WebSiteEntity, ZoneEntity]]:
    """
    This query computes zone dependencies of every website in the database.
    Missing information regarding a website are simply ignored.
    Example: the HTTP server associated to a website xyz is NULL, the remaining dependencies regarding xyz will be
    written in the result.

    """
    web_site_entities = helper_web_site.get_everyone()
    print(f"Parameters: {len(web_site_entities)} web sites retrieved from database.")
    result = list()
    for chunk in chunked(web_site_entities, 400):
        with db.atomic():       # peewee transaction
            for web_site_entity in chunk:
                # getting webservers and domain name associated to website
                try:
                    https_web_server_entity, http_web_server_entity = helper_web_server.get_from(web_site_entity)
                except NoDisposableRowsError:
                    print(f"!!! unresolvable webservers of website: {web_site_entity.url.string} !!!")
                    continue
                try:
                    web_site_domain_name_entity = helper_domain_name.get_of(web_site_entity)
                except DoesNotExist:
                    print(f"!!! unresolvable domain name associated to website: {web_site_entity.url.string} !!!")
                    raise
                # zone dependencies of webservers
                zone_dependencies_of_web_site = set()
                if https_web_server_entity is None:
                    pass
                else:
                    zes = helper_zone.get_zone_dependencies_of_entity_domain_name(https_web_server_entity.name)
                    for ze in zes:
                        zone_dependencies_of_web_site.add(ze)
                if http_web_server_entity != https_web_server_entity:
                    if http_web_server_entity is None:
                        pass
                    else:
                        zes = helper_zone.get_zone_dependencies_of_entity_domain_name(http_web_server_entity.name)
                        for ze in zes:
                            zone_dependencies_of_web_site.add(ze)
                # zone dependencies of website
                zes = helper_zone.get_zone_dependencies_of_entity_domain_name(web_site_domain_name_entity)
                for ze in zes:
                    zone_dependencies_of_web_site.add(ze)
                for ze in zone_dependencies_of_web_site:
                    result.append((web_site_entity, ze))
    return result


def do_query_5() -> List[Tuple[MailDomainEntity, ZoneEntity]]:
    """
    This query computes zone dependencies of every mail domain in the database.

    """
    mail_domain_entities = helper_mail_domain.get_everyone()
    print(f"Parameters: {len(mail_domain_entities)} mail domains retrieved from database.")
    result = list()
    for chunk in chunked(mail_domain_entities, 400):
        with db.atomic():       # peewee transaction
            for mail_domain_entity in chunk:
                # getting mail servers
                try:
                    mail_server_entities_of_mail_domain = helper_mail_server.get_every_of(mail_domain_entity)
                except DoesNotExist:
                    print(f"!!! unresolvable mailservers of maildomain: {mail_domain_entity.name.string} !!!")
                    continue
                zone_dependencies_of_web_site = set()
                # zone dependencies of mail domain
                zes = helper_zone.get_zone_dependencies_of_entity_domain_name(mail_domain_entity.name)
                for ze in zes:
                    zone_dependencies_of_web_site.add(ze)
                # zone dependencies of mail servers
                for mail_server_entity in mail_server_entities_of_mail_domain:
                    zes = helper_zone.get_zone_dependencies_of_entity_domain_name(mail_server_entity.name)
                    for ze in zes:
                        zone_dependencies_of_web_site.add(ze)
                for ze in zone_dependencies_of_web_site:
                    result.append((mail_domain_entity, ze))
    return result


def do_query_6() -> List[Tuple[MailDomainEntity, Set[IpAddressEntity], Set[IpNetworkEntity], Set[AutonomousSystemEntity]]]:
    """
    This query computes data regarding the architecture of every mail domain in the database.

    """
    mail_domain_entities = helper_mail_domain.get_everyone()
    print(f"Parameters: {len(mail_domain_entities)} mail domains retrieved from database.")
    result = list()
    for chunk in chunked(mail_domain_entities, 400):
        with db.atomic():       # peewee transaction
            for mail_domain_entity in chunk:
                # getting mail servers
                try:
                    mail_server_entities_of_mail_domain = helper_mail_server.get_every_of(mail_domain_entity)
                except DoesNotExist:
                    print(f"!!! unresolvable mailservers of maildomain: {mail_domain_entity.name.string} !!!")
                    continue
                #
                ip_addresses_of_mail_domain = set()
                ip_networks_of_mail_domain = set()
                autonomous_systems_of_mail_domain = set()
                for mail_server_entity in mail_server_entities_of_mail_domain:
                    try:
                        cname_chain, iaes = helper_domain_name.resolve_a_path(mail_server_entity.name, as_persistence_entities=True)
                    except NoAvailablePathError:
                        print(f"!!! unresolvable A path from mailserver {mail_server_entity.name.string} associated to maildomain: {mail_domain_entity.name.string} !!!")
                        continue
                    for iae in iaes:
                        ip_addresses_of_mail_domain.add(iae)
                        try:
                            ine = helper_ip_network.get_of(iae)
                        except DoesNotExist:
                            print(f"!!! unresolvable network from IP address {iae.exploded_notation} of mailserver {mail_server_entity.name.string} associated to maildomain: {mail_domain_entity.name.string} !!!")
                            raise
                        ip_networks_of_mail_domain.add(ine)
                        try:
                            ase = helper_autonomous_system.get_of_ip_address(iae)
                        except DoesNotExist:
                            print(f"!!! unresolvable AS from IP address {iae.exploded_notation} of mailserver {mail_server_entity.name.string} associated to maildomain: {mail_domain_entity.name.string} !!!")
                            raise
                        autonomous_systems_of_mail_domain.add(ase)
                result.append((mail_domain_entity, ip_addresses_of_mail_domain, ip_networks_of_mail_domain, autonomous_systems_of_mail_domain))
    return result


def do_query_7() -> List[Tuple[WebServerEntity, Set[IpAddressEntity], Set[IpNetworkEntity], Set[AutonomousSystemEntity]]]:
    """
    This query computes data regarding the architecture of every webserver in the database.

    """
    web_server_entities = helper_web_server.get_everyone()
    print(f"Parameters: {len(web_server_entities)} web servers retrieved from database.")
    result = list()
    for chunk in chunked(web_server_entities, 400):
        with db.atomic():       # peewee transaction
            for web_server_entity in chunk:
                ip_addresses_of_web_server = set()
                ip_networks_of_web_server = set()
                autonomous_systems_of_web_server = set()
                try:
                    cname_chain, iaes = helper_domain_name.resolve_a_path(web_server_entity.name, as_persistence_entities=True)
                except NoAvailablePathError:
                    print(f"!!! unresolvable A path from webserver {web_server_entity.name.string} !!!")
                    continue
                for iae in iaes:
                    ip_addresses_of_web_server.add(iae)
                    try:
                        ine = helper_ip_network.get_of(iae)
                    except DoesNotExist:
                        print(f"!!! unresolvable network from IP address {iae.exploded_notation} of webserver {web_server_entity.name.string} !!!")
                        raise
                    ip_networks_of_web_server.add(ine)
                    try:
                        ase = helper_autonomous_system.get_of_ip_address(iae)
                    except DoesNotExist:
                        print(f"!!! unresolvable AS from IP address {iae.exploded_notation} of webserver {web_server_entity.name.string} !!!")
                        raise
                    autonomous_systems_of_web_server.add(ase)
                result.append((web_server_entity, ip_addresses_of_web_server, ip_networks_of_web_server, autonomous_systems_of_web_server))
    return result


#TODO
def do_query_8() -> List[Tuple[IpNetworkEntity, AutonomousSystemEntity, Set[WebServerEntity], Set[MailServerEntity], Set[NameServerEntity], Set[ZoneEntity], Set[WebSiteEntity], Set[MailDomainEntity]]]:
    """
    Network query...

    """
    network_entities = helper_ip_network.get_everyone()
    print(f"Parameters: {len(network_entities)} IP networks retrieved from database.")
    result = list()
    for chunk in chunked(network_entities, 400):
        with db.atomic():       # peewee transaction
            for network_entity in chunk:
                try:
                    autonomous_system = helper_autonomous_system.get_of_entity_ip_network(network_entity)
                except DoesNotExist:
                    print(f"!!! unresolvable AS from IP network {network_entity.exploded_notation} !!!")
                    continue
                try:
                    dnes = helper_domain_name.get_everyone_from_ip_network(network_entity)
                except NoDisposableRowsError:
                    print(f"!!! unresolvable domain names from IP network {network_entity.exploded_notation} !!!")
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
