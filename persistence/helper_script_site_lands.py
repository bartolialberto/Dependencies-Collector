from persistence.BaseModel import ScriptSiteEntity, ScriptServerEntity, IpAddressEntity, ScriptSiteLandsAssociation


def insert(ssitee: ScriptSiteEntity, sservere: ScriptServerEntity or None, https: bool, iae: IpAddressEntity or None) -> ScriptSiteLandsAssociation:
    ssla, created = ScriptSiteLandsAssociation.get_or_create(script_site=ssitee, script_server=sservere, https=https, ip_address=iae)
    return ssla