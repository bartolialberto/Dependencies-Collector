from persistence.BaseModel import IpAddressDependsAssociation, IpAddressEntity, IpNetworkEntity, IpRangeTSVEntity, \
    IpRangeROVEntity


def insert(iae: IpAddressEntity, ine: IpNetworkEntity or None, irte: IpRangeTSVEntity or None, irre: IpRangeROVEntity or None) -> IpAddressDependsAssociation:
    iada, created = IpAddressDependsAssociation.get_or_create(ip_address=iae, ip_network=ine, ip_range_tsv=irte, ip_range_rov=irre)
    return iada
