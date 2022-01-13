from persistence.BaseModel import BelongsAssociation, IpNetworkEntity, AutonomousSystemEntity


def insert(ine: IpNetworkEntity, ase: AutonomousSystemEntity) -> BelongsAssociation:
    ba, created = BelongsAssociation.get_or_create(ip_network=ine, autonomous_system=ase)
    return ba
