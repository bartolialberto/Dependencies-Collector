from persistence.BaseModel import EntryIpAsDatabaseEntity, HasAssociation, IpRangeEntity


def insert(eiade: EntryIpAsDatabaseEntity, ire: IpRangeEntity) -> HasAssociation:
    ha, created = HasAssociation.get_or_create(entry=eiade, range=ire)
    return ha
