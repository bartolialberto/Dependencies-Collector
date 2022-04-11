from typing import Tuple
from peewee import DoesNotExist
from entities.DomainName import DomainName
from persistence import helper_domain_name
from persistence.BaseModel import ScriptServerEntity, DomainNameEntity


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
