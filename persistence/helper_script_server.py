from persistence import helper_url, helper_domain_name
from persistence.BaseModel import ScriptServerEntity
from utils import domain_name_utils


def insert(name: str) -> ScriptServerEntity:
    dn = domain_name_utils.insert_trailing_point(name)
    dne = helper_domain_name.insert(dn)
    sse, created = ScriptServerEntity.get_or_create(name=dne)
    return sse
