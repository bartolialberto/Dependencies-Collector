from persistence.BaseModel import IpAddressDependsAssociation, IpAddressEntity, IpNetworkEntity


def insert(iae: IpAddressEntity, ine: IpNetworkEntity or None) -> IpAddressDependsAssociation:
    iada, created = IpAddressDependsAssociation.get_or_create(ip_address=iae, ip_network=ine)
    return iada
