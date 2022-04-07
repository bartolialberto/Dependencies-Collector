from persistence.BaseModel import DomainNameEntity, ScriptSiteEntity, ScriptSiteDomainNameAssociation


def insert(wse: ScriptSiteEntity, dne: DomainNameEntity) -> ScriptSiteDomainNameAssociation:
    ssdna, created = ScriptSiteDomainNameAssociation.get_or_create(script_site=wse, domain_name=dne)
    return ssdna
