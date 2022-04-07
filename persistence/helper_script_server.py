from typing import Tuple, Set
from peewee import DoesNotExist
from entities.DomainName import DomainName
from persistence import helper_domain_name
from persistence.BaseModel import ScriptServerEntity, ScriptSiteLandsAssociation, ScriptHostedOnAssociation, \
    ScriptWithdrawAssociation, DomainNameEntity, WebSiteEntity, ScriptSiteEntity


def insert(name: DomainName) -> ScriptServerEntity:
    dne = helper_domain_name.insert(name)
    sse, created = ScriptServerEntity.get_or_create(name=dne)
    return sse


def get(web_server: DomainName) -> Tuple[ScriptServerEntity, DomainNameEntity]:
    try:
        dne = helper_domain_name.get(web_server)
    except DoesNotExist:
        raise
    try:
        sse = ScriptServerEntity.get(ScriptServerEntity.name == dne)
    except DoesNotExist:
        raise
    return sse, dne


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
