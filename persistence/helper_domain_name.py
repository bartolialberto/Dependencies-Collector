from peewee import DoesNotExist
from exceptions.InvalidDomainNameError import InvalidDomainNameError
from persistence import helper_ip_address, helper_alias
from persistence.BaseModel import DomainNameEntity, IpAddressEntity
from utils import domain_name_utils


def insert(string: str) -> DomainNameEntity:
    dn = domain_name_utils.insert_trailing_point(string)
    try:
        domain_name_utils.grammatically_correct(dn)
    except InvalidDomainNameError:
        raise
    dne, created = DomainNameEntity.get_or_create(name=dn)
    return dne


def get(domain_name: str) -> DomainNameEntity:
    dn = domain_name_utils.insert_trailing_point(domain_name)
    try:
        return DomainNameEntity.get_by_id(dn)
    except DoesNotExist:
        raise


def resolve_access_path(dne: DomainNameEntity) -> IpAddressEntity:
    try:
        iae = helper_ip_address.get_first_of(dne)
        return iae
    except DoesNotExist:
        pass
    try:
        adnes = helper_alias.get_all_aliases_from_entity(dne)
    except DoesNotExist:
        raise
    for adne in adnes:
        try:
            return resolve_access_path(adne)
        except DoesNotExist:
            pass
    raise DoesNotExist


