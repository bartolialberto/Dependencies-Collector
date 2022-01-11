from persistence.BaseModel import ScriptEntity, ScriptSiteEntity, ScriptHostedOnAssociation


def insert(se: ScriptEntity, sse: ScriptSiteEntity) -> ScriptHostedOnAssociation:
    shoa, created = ScriptHostedOnAssociation.get_or_create(script=se, script_site=sse)
    return shoa
