from persistence.BaseModel import IpNetworkEntity, PrefixAssociation, EntryROVPageEntity


def insert(e: EntryROVPageEntity, n: IpNetworkEntity) -> PrefixAssociation:
    pa, created = PrefixAssociation.get_or_create(entry=e.id, network=n.id)
    return pa
