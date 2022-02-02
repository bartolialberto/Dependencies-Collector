from persistence.BaseModel import PrefixesTableAssociation, ROVEntity, AutonomousSystemEntity, \
    IpRangeROVEntity


def insert(irre: IpRangeROVEntity or None, re: ROVEntity or None, ase: AutonomousSystemEntity) -> PrefixesTableAssociation:
    pta, created = PrefixesTableAssociation.get_or_create(ip_range_rov=irre, rov=re, autonomous_system=ase)
    return pta
