from typing import List, Set
from peewee import DoesNotExist
from persistence import helper_script_site
from persistence.BaseModel import ScriptSiteEntity, ScriptServerEntity, IpAddressEntity, ScriptSiteLandsAssociation


def insert(ssitee: ScriptSiteEntity, sservere: ScriptServerEntity or None, https: bool, iae: IpAddressEntity or None) -> ScriptSiteLandsAssociation:
    ssla, created = ScriptSiteLandsAssociation.get_or_create(script_site=ssitee, script_server=sservere, https=https, ip_address=iae)
    return ssla


def get_all_from_script_site_string(url: str) -> List[ScriptSiteLandsAssociation]:
    try:
        sse = helper_script_site.get(url)
    except DoesNotExist:
        raise
    result = list()
    query = ScriptSiteLandsAssociation.select()\
        .join_from(ScriptSiteLandsAssociation, ScriptSiteEntity)\
        .where(ScriptSiteLandsAssociation.script_site == sse)
    for row in query:
        result.append(row)
    return result


def get_all_from_script_site_entity(sse: ScriptSiteEntity) -> List[ScriptSiteLandsAssociation]:
    result = list()
    query = ScriptSiteLandsAssociation.select()\
        .join_from(ScriptSiteLandsAssociation, ScriptSiteEntity)\
        .where(ScriptSiteLandsAssociation.script_site == sse)
    for row in query:
        result.append(row)
    return result


def delete_all_from_script_site_entity(sse: ScriptSiteEntity):
    try:
        tmp = get_all_from_script_site_entity(sse)
        for relation in tmp:
            relation.delete_instance()
    except DoesNotExist:
        pass


def get_unresolved() -> Set[ScriptSiteEntity]:
    query = ScriptSiteLandsAssociation.select()\
        .join_from(ScriptSiteLandsAssociation, ScriptSiteEntity)\
        .where((ScriptSiteLandsAssociation.script_server == None) and (ScriptSiteLandsAssociation.ip_address == None))
    result = set()
    for row in query:
        result.add(row.script_site)
    return result
