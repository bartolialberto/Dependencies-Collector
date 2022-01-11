from persistence.BaseModel import WebSiteEntity, ScriptEntity, ScriptWithdrawAssociation


def insert(wse: WebSiteEntity, se: ScriptEntity or None, https: bool, integrity: str or None) -> ScriptWithdrawAssociation:
    swa, created = ScriptWithdrawAssociation.get_or_create(script=se, web_site=wse, integrity=integrity, https=https)
    return swa
