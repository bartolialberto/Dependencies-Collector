from typing import List, Tuple
from peewee import DoesNotExist
from persistence import helper_domain_name, helper_script_site, helper_web_site
from persistence.BaseModel import ScriptServerEntity, ScriptSiteLandsAssociation, ScriptHostedOnAssociation, \
    ScriptWithdrawAssociation, DomainNameEntity
from utils import domain_name_utils


def insert(name: str) -> Tuple[ScriptServerEntity, DomainNameEntity]:
    dn = domain_name_utils.insert_trailing_point(name)
    dne = helper_domain_name.insert(dn)
    sse, created = ScriptServerEntity.get_or_create(name=dne)
    return sse, dne


def get(web_server: str) -> ScriptServerEntity:
    try:
        dne = helper_domain_name.get(web_server)
    except DoesNotExist:
        raise
    try:
        return ScriptServerEntity.get(ScriptServerEntity.name == dne)
    except DoesNotExist:
        raise


def get_from_string_web_site(web_site: str):
    try:
        wse = helper_web_site.get(web_site)
    except DoesNotExist:
        raise
    query = ScriptSiteLandsAssociation.select()\
        .join(ScriptHostedOnAssociation, on=(ScriptSiteLandsAssociation.script_site == ScriptHostedOnAssociation.script_site))\
        .join(ScriptWithdrawAssociation, on=(ScriptHostedOnAssociation.script == ScriptWithdrawAssociation.script))\
        .where((ScriptWithdrawAssociation.web_site == wse) & (ScriptSiteLandsAssociation.script_server.is_null(False)))
    result = set()
    for row in query:
        result.add(row.script_server)
    return result


def get_from_string_script_site(script_site_param: str, https: bool, first_only: bool) -> List[ScriptServerEntity] or ScriptServerEntity:
    sse = None
    query = None
    try:
        sse = helper_script_site.get(script_site_param)
    except DoesNotExist:
        raise
    if first_only:
        query = ScriptSiteLandsAssociation.select() \
            .join_from(ScriptSiteLandsAssociation, ScriptServerEntity) \
            .where((ScriptSiteLandsAssociation.script_site == sse), (ScriptSiteLandsAssociation.https == https))\
            .limit(1)
        for row in query:
            return row.web_server
        raise DoesNotExist
    else:
        query = ScriptSiteLandsAssociation.select()\
            .join_from(ScriptSiteLandsAssociation, ScriptServerEntity)\
            .where((ScriptSiteLandsAssociation.script_site == sse), (ScriptSiteLandsAssociation.https == https))
        result = list()
        for row in query:
            result.append(row.script_server)
        return result
