from persistence.BaseModel import EntryIpAsDatabaseEntity, IpRangeEntity, HasAssociation


def insert_or_get(entry: EntryIpAsDatabaseEntity, ip_range: IpRangeEntity) -> HasAssociation:
    h, created = HasAssociation.get_or_create(entry=entry.id, range=ip_range)
    return h
