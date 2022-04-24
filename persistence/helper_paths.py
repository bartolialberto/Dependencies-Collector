from ipaddress import IPv4Address
from typing import Tuple, List, Set
from entities.DomainName import DomainName
from entities.paths.APath import APath
from entities.paths.MXPath import MXPath
from entities.paths.NSPath import NSPath
from persistence import helper_domain_name, helper_alias, helper_ip_address, helper_access, helper_mail_domain, \
    helper_mail_server, helper_mail_domain_composed, helper_zone, helper_name_server, helper_zone_composed, \
    helper_alias_to_zone
from persistence.BaseModel import DomainNameEntity, IpAddressEntity, MailDomainEntity, MailServerEntity, ZoneEntity, \
    NameServerEntity


def insert_a_path(a_path: APath) -> Tuple[List[DomainNameEntity], Set[IpAddressEntity]]:
    cname_chain_entities = list()
    addresses_entities = set()
    for rr in a_path.get_cname_chain():
        dn_entity_from = helper_domain_name.insert(rr.name)
        dn_entity_to = helper_domain_name.insert(rr.get_first_value())
        helper_alias.insert(dn_entity_from, dn_entity_to)
        cname_chain_entities.append(dn_entity_from)
    dne_canonical = helper_domain_name.insert(a_path.get_resolution().name)
    cname_chain_entities.append(dne_canonical)
    for value in a_path.get_resolution().values:
        ipe = helper_ip_address.insert(value)
        helper_access.insert(dne_canonical, ipe)
        addresses_entities.add(ipe)
    return cname_chain_entities, addresses_entities


def insert_a_path_for_mail_servers(a_path: APath, mail_domain_entity: MailDomainEntity) -> Tuple[MailServerEntity, List[DomainNameEntity], Set[IpAddressEntity]]:
    aliases_chain = list()
    addresses = set()
    if len(a_path.get_cname_chain()) == 0:
        mse = helper_mail_server.insert(a_path.get_resolution().name)
        helper_mail_domain_composed.insert(mail_domain_entity, mse)
        dne_canonical = mse.name
    else:
        mse = helper_mail_server.insert(a_path.get_cname_chain()[0].name)
        helper_mail_domain_composed.insert(mail_domain_entity, mse)
        dn_entity_to = helper_domain_name.insert(a_path.get_cname_chain()[0].get_first_value())
        helper_alias.insert(mse.name, dn_entity_to)
        aliases_chain.append(mse.name)
        for rr in a_path.get_cname_chain()[1:]:
            dn_entity_from = helper_domain_name.insert(rr.name)
            dn_entity_to = helper_domain_name.insert(rr.get_first_value())
            helper_alias.insert(dn_entity_from, dn_entity_to)
            aliases_chain.append(dn_entity_from)
        dne_canonical = helper_domain_name.insert(a_path.get_resolution().name)
    aliases_chain.append(dne_canonical)
    for value in a_path.get_resolution().values:
        ipe = helper_ip_address.insert(value)
        helper_access.insert(dne_canonical, ipe)
        addresses.add(ipe)
    return mse, aliases_chain, addresses


def insert_mx_path(mx_path: MXPath) -> Tuple[List[DomainNameEntity], MailDomainEntity, Set[MailServerEntity]]:
    cname_chain_entities = list()
    mail_servers_entities = set()
    for rr in mx_path.get_cname_chain():
        dn_entity_from = helper_domain_name.insert(rr.name)
        dn_entity_to = helper_domain_name.insert(rr.get_first_value())
        helper_alias.insert(dn_entity_from, dn_entity_to)
        cname_chain_entities.append(dn_entity_from)
    mail_domain_entity = helper_mail_domain.insert(mx_path.get_resolution().name)
    for value in mx_path.get_resolution().values:
        if isinstance(value, DomainName):
            mail_server_entity = helper_mail_server.insert(value)
            helper_mail_domain_composed.insert(mail_domain_entity, mail_server_entity)
            mail_servers_entities.add(mail_server_entity)
        elif isinstance(value, IPv4Address):
            # TODO: NOT HANDLED: MX RR has an IP address as value
            pass
        else:
            raise ValueError
    return cname_chain_entities, mail_domain_entity, mail_servers_entities


def insert_ns_path(ns_path: NSPath) -> Tuple[List[DomainNameEntity], ZoneEntity, Set[NameServerEntity]]:
    cname_chain_entities = list()
    name_servers_entities = set()
    last_domain_entity = None
    for i, rr in enumerate(ns_path.get_cname_chain()):
        dn_entity_from = helper_domain_name.insert(rr.name)
        dn_entity_to = helper_domain_name.insert(rr.get_first_value())
        if i == len(ns_path.get_cname_chain()) - 1:
            last_domain_entity = dn_entity_from
        else:
            helper_alias.insert(dn_entity_from, dn_entity_to)
            cname_chain_entities.append(dn_entity_from)
    zone_entity = helper_zone.insert(ns_path.get_resolution().name)
    if last_domain_entity is not None:
        helper_alias_to_zone.insert(zone_entity, last_domain_entity)
    for value in ns_path.get_resolution().values:
        nse = helper_name_server.insert(value)
        helper_zone_composed.insert(zone_entity, nse)
        name_servers_entities.add(nse)
    return cname_chain_entities, zone_entity, name_servers_entities
