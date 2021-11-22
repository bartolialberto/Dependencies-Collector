from persistence.BaseModel import NameserverEntity


def insert_or_get(name: str, ip: str) -> NameserverEntity:
    n, created = NameserverEntity.get_or_create(name=name, ip=ip)
    return n
