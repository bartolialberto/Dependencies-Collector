import ipaddress
from typing import List, Tuple


class EntryIpAsDatabase:
    """
    This class represent an entry in the database as describe in https://iptoasn.com/g.

    ...

    Attributes
    ----------
    start_ip_range : ipaddress.IPv4Address
        The start of the ip range. It's an ip address.
    end_ip_range : ipaddress.IPv4Address
        The end of the ip range. It's an ip address.
    as_number : int
        The Autonomous System number. It's a number.
    country_code : str
        Should be the country code.
    as_description : str
        Should be the Autonomous System brief description.
    """
    def __init__(self, entries_inline: List[str]):
        """
        Instantiate a EntryIpAsDatabase object from a list of string follow format described in
        https://iptoasn.com/; list probably split with a character separator from an entire single string.

        :param entries_inline: List of string to associate to each entity of the entry.
        :type entries_inline: List[str]
        :raises ValueError: If the number of entities is not correct (5).
        If entry.start_ip_range is not a valid ipaddress.Ipv4Address.
        If entry.end_ip_range is not a valid ipaddress.Ipv4Address.
        If entry.as_number is not a valid integer number.
        """
        if len(entries_inline) != 5:
            raise ValueError
        string_start_ip_range = entries_inline[0]
        string_end_ip_range = entries_inline[1]
        string_as_number = entries_inline[2]
        string_country_code = entries_inline[3]
        string_as_description = entries_inline[4]

        try:
            tmp = ipaddress.IPv4Address(string_start_ip_range)
            self.start_ip_range = tmp
        except ValueError:
            raise
        try:
            tmp = ipaddress.IPv4Address(string_end_ip_range)
            self.end_ip_range = tmp
        except ValueError:
            raise
        try:
            tmp = int(string_as_number)
            self.as_number = tmp
        except ValueError:
            raise
        self.country_code = string_country_code
        self.as_description = string_as_description

    def get_all_networks(self) -> List[ipaddress.IPv4Network]:
        """
        Returns a list of networks from the summarized network range given the first and last IP addresses of the range
        in the entry (self object).

        :raise TypeError: If first or last are not IP addresses or are not of the same version.
        :raise ValueError: If last is not greater than first or if first address version is not 4 or 6
        :returns: A list of valid ipaddress.IPv4Network.
        :rtype: List[ipaddress.IPv4Network]
        """
        try:
            return list(ipaddress.summarize_address_range(self.start_ip_range, self.end_ip_range))
        except (TypeError, ValueError):
            raise

    def get_network_of_ip(self, ip: ipaddress.IPv4Address) -> Tuple[ipaddress.IPv4Network, List[ipaddress.IPv4Network]]:
        """
        Return the network from the summarized network range given the first and last IP addresses of the range in the
        entry (self object), and all the networks associated with such range.

        :param ip: Ip address.
        :type ip: ipaddress.IPv4Address
        :raise TypeError: If first or last are not IP addresses or are not of the same version.
        :raise ValueError: If last is not greater than first or if first address version is not 4 or 6.
        If there's not a network in which is contained the ip address parameter.
        :returns: A tuple containing the belonging network first and then all the networks.
        :rtype: Tuple[ipaddress.IPv4Network, List[ipaddress.IPv4Network]]
        """
        try:
            networks = self.get_all_networks()
        except (TypeError, ValueError):
            raise
        for network in networks:
            if ip in network:
                return network, networks
        raise ValueError()

    def __str__(self) -> str:
        """
        This method returns a human-readable string representation of this object.

        :return: A human-readable string representation of this object.
        :rtype: str
        """
        return f"{str(self.start_ip_range)}\t{str(self.end_ip_range)}\t{str(self.as_number)}\t{self.country_code}\t{self.as_description}"

    def __eq__(self, other) -> bool:
        """
        This method returns a boolean for comparing 2 objects equality.

        :param other:
        :return: The result of the comparison.
        :rtype: bool
        """
        if isinstance(other, EntryIpAsDatabase):
            return self.as_number == other.as_number
        else:
            return False

    def __hash__(self) -> int:
        """
        This method returns the hash of this object. Should be defined alongside the __eq__ method with the same
        returning value from 2 objects.

        :return: Hash of this object.
        :rtype: int
        """
        return hash((self.as_number, self.start_ip_range, self.end_ip_range))
