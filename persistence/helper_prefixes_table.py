from persistence.BaseModel import PrefixesTableAssociation, IpNetworkEntity, ROVEntity, AutonomousSystemEntity


def insert(ine: IpNetworkEntity, re: ROVEntity, ase: AutonomousSystemEntity) -> PrefixesTableAssociation:
    pta, created = PrefixesTableAssociation.get_or_create(ip_network=ine, rov=re, autonomous_system=ase)
    return pta
