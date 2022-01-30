from peewee import DoesNotExist
from persistence import helper_script_site
from persistence.BaseModel import DomainNameEntity, ScriptSiteEntity, ScriptSiteDomainNameAssociation


def insert(wse: ScriptSiteEntity, dne: DomainNameEntity) -> ScriptSiteDomainNameAssociation:
    ssdna, created = ScriptSiteDomainNameAssociation.get_or_create(script_site=wse, domain_name=dne)
    return ssdna


def get_from_string_script_site(web_site: str) -> ScriptSiteDomainNameAssociation:
    try:
        sse = helper_script_site.get(web_site)
    except DoesNotExist:
        raise
    return get_from_entity_script_site(sse)


def get_from_entity_script_site(sse: ScriptSiteEntity) -> ScriptSiteDomainNameAssociation:
    try:
        ssdna = ScriptSiteDomainNameAssociation.get(ScriptSiteDomainNameAssociation.script_site == sse)
    except DoesNotExist:
        raise
    return ssdna
