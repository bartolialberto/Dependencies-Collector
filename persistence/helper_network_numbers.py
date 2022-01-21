from persistence.BaseModel import NetworkNumbersAssociation, IpRangeTSVEntity, AutonomousSystemEntity


def insert(irte: IpRangeTSVEntity, ase: AutonomousSystemEntity) -> NetworkNumbersAssociation:
    nna, created = NetworkNumbersAssociation.get_or_create(ip_range_tsv=irte, autonomous_system=ase)
    return nna
