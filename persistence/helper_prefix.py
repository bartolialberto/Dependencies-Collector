from persistence.BaseModel import EntryROVPageEntity, IpNetworkEntity, PrefixAssociation


def insert(e: EntryROVPageEntity, n: IpNetworkEntity) -> PrefixAssociation:
    pa, created = PrefixAssociation.get_or_create(entry=e.id, network=n.id)
    return pa