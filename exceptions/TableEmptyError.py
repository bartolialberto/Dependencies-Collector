from ipaddress import IPv4Address


class TableEmptyError(Exception):
    message: str
    in_as: int
    for_ip_address: IPv4Address

    def __init__(self, as_number: int, for_ip_address=None):
        if for_ip_address is None:
            temp = f"Found empty table in ROV page for AS number: {as_number}."
        else:
            temp = f"Found empty table in AS{as_number} ROV page for IP address: {str(for_ip_address.exploded)}."
        self.in_as = as_number
        self.for_ip_address = for_ip_address
        self.message = temp
        BaseException.__init__(self, temp)

    def __str__(self):
        return f'{self.message}'
