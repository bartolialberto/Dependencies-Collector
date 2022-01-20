from typing import List
from peewee import DoesNotExist
from persistence import helper_url, helper_domain_name, helper_script_site
from persistence.BaseModel import ScriptServerEntity, ScriptSiteEntity, ScriptSiteLandsAssociation
from utils import domain_name_utils


def insert(name: str) -> ScriptServerEntity:
    dn = domain_name_utils.insert_trailing_point(name)
    dne = helper_domain_name.insert(dn)
    sse, created = ScriptServerEntity.get_or_create(name=dne)
    return sse


def get_from(script_site_param: str or ScriptSiteEntity, https: bool, first_only: bool) -> List[ScriptServerEntity] or ScriptServerEntity:
    sse = None
    query = None
    if isinstance(script_site_param, ScriptSiteEntity):
        sse = script_site_param
    else:
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
