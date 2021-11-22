from persistence.BaseModel import IpNetworkEntity, EntryIpAsDatabaseEntity, BelongingNetworkAssociation


def insert_or_get(as_number: int, n: IpNetworkEntity):
    e = EntryIpAsDatabaseEntity.get(EntryIpAsDatabaseEntity.autonomous_system_number == as_number)
    BelongingNetworkAssociation.get_or_create(entry=e.id, network=n.id)
