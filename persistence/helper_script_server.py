from typing import List, Tuple, Set
from peewee import DoesNotExist
from persistence import helper_domain_name, helper_script_site, helper_web_site
from persistence.BaseModel import ScriptServerEntity, ScriptSiteLandsAssociation, ScriptHostedOnAssociation, \
    ScriptWithdrawAssociation, DomainNameEntity, WebSiteEntity, ScriptSiteEntity
from utils import domain_name_utils


def insert(name: str) -> Tuple[ScriptServerEntity, DomainNameEntity]:
    dn = domain_name_utils.insert_trailing_point(name)
    dne = helper_domain_name.insert(dn)
    sse, created = ScriptServerEntity.get_or_create(name=dne)
    return sse, dne


def get(web_server: str) -> Tuple[ScriptServerEntity, DomainNameEntity]:
    try:
        dne = helper_domain_name.get(web_server)
    except DoesNotExist:
        raise
    try:
        sse = ScriptServerEntity.get(ScriptServerEntity.name == dne)
    except DoesNotExist:
        raise
    return sse, dne


def get_from_string_web_site(web_site: str):
    try:
        wse = helper_web_site.get(web_site)
    except DoesNotExist:
        raise
    return get_from_entity_web_site(wse)


def get_from_entity_web_site(wse: WebSiteEntity) -> Set[ScriptServerEntity]:
    query = ScriptSiteLandsAssociation.select()\
        .join(ScriptHostedOnAssociation, on=(ScriptSiteLandsAssociation.script_site == ScriptHostedOnAssociation.script_site))\
        .join(ScriptWithdrawAssociation, on=(ScriptHostedOnAssociation.script == ScriptWithdrawAssociation.script))\
        .where((ScriptWithdrawAssociation.web_site == wse) & (ScriptSiteLandsAssociation.script_server.is_null(False)))
    result = set()
    for row in query:
        result.add(row.script_server)
    return result


def get_from_entity_script_site(sse: ScriptSiteEntity) -> Set[ScriptServerEntity]:
    query = ScriptSiteLandsAssociation.select()\
        .where((ScriptSiteLandsAssociation.script_site == sse) & (ScriptSiteLandsAssociation.script_server.is_null(False)))
    result = set()
    for row in query:
        result.add(row.script_server)
    return result


def get_from_string_script_site_and_scheme(script_site: str, https: bool) -> ScriptServerEntity:
    try:
        sse = helper_script_site.get(script_site)
    except DoesNotExist:
        raise
    return get_from_entity_script_site_and_scheme(sse, https)


def get_from_entity_script_site_and_scheme(sse: ScriptSiteEntity, https: bool) -> ScriptServerEntity:
    try:
        ssla = ScriptSiteLandsAssociation.get((ScriptSiteLandsAssociation.script_site == sse) & (ScriptSiteLandsAssociation.https == https) & (ScriptSiteLandsAssociation.script_server.is_null(False)))
    except DoesNotExist:
        raise
    return ssla.script_server


def get_all_from_string_script_site_and_scheme(script_site_param: str, https: bool) -> List[ScriptServerEntity]:
    """ Query probably useful only for tests. """
    try:
        sse = helper_script_site.get(script_site_param)
    except DoesNotExist:
        raise
    query = ScriptSiteLandsAssociation.select()\
        .where((ScriptSiteLandsAssociation.script_site == sse) & (ScriptSiteLandsAssociation.https == https) & (ScriptSiteLandsAssociation.script_server.is_null(False)))
    result = list()
    for row in query:
        result.append(row.script_server)
    return result
