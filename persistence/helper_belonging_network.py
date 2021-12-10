from persistence.BaseModel import IpNetworkEntity, EntryIpAsDatabaseEntity, BelongingNetworkAssociation


def insert_from_as_number(as_number: int, n: IpNetworkEntity):
    e = EntryIpAsDatabaseEntity.get(EntryIpAsDatabaseEntity.autonomous_system_number == as_number)
    BelongingNetworkAssociation.get_or_create(entry=e.id, network=n.id)


def insert(ee: EntryIpAsDatabaseEntity, ine: IpNetworkEntity) -> BelongingNetworkAssociation:
    bne, created = BelongingNetworkAssociation.get_or_create(entry=ee, network=ine)
    return bne
