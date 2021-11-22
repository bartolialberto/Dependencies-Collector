from entities.RRecord import RRecord
from entities.TypesRR import TypesRR
from entities.Zone import Zone
from persistence.BaseModel import ZoneEntity, BelongsAssociation, NameserverEntity


def get(zone_name: str) -> Zone:
    query = ZoneEntity.select().where(ZoneEntity.name == zone_name)
    for row in query:
        # q = Belongs.select().join_from(Belongs, NameserverEntity).where(Belongs.nameserver_id == row.id)
        q = NameserverEntity.select().join(BelongsAssociation).where(BelongsAssociation.zone_id == row.id)
        nameservers = list()
        for r in q:
            tmp = RRecord(r.name, TypesRR.A, r.ip)
            nameservers.append(tmp)
        return Zone(zone_name, nameservers, [])
