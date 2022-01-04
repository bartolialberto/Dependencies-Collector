from persistence.BaseModel import DomainNameEntity, IpAddressEntity, AccessAssociation


def insert(dne: DomainNameEntity, iae: IpAddressEntity) -> AccessAssociation:
    aa, created = AccessAssociation.get_or_create(domain_name=dne, ip_address=iae)
    return aa
