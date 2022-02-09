import unittest
from peewee import DoesNotExist
from exceptions.NoAvailablePathError import NoAvailablePathError
from persistence import helper_ip_network, helper_domain_name, helper_ip_address


class NetworkQueryTestCase(unittest.TestCase):
    def test_1_query_networks_from_domain_name(self):
        print(f"\n------- [1] QUERY NETWORKS FROM DOMAIN NAME -------")
        # PARAMETER
        domain_name = 'platform.twitter.com.'
        domain_name = 'ossigeno.acantho.sys.'
        # QUERY
        print(f"Parameter: {domain_name}")
        try:
            dne = helper_domain_name.get(domain_name)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        try:
            ines = helper_ip_network.get_of_entity_domain_name(dne)
        except (NoAvailablePathError, DoesNotExist) as e:
            self.fail(f"!!! {str(e)} !!!")
        for i, ine in enumerate(ines):
            print(f"network[{i+1}/{len(ines)}]: {ine.compressed_notation}")
        print(f"------- [1] END QUERY NETWORKS FROM DOMAIN NAME -------")

    def test_2_query_domain_names_from_network(self):
        print(f"\n------- [2] QUERY DOMAIN NAMES FROM NETWORK -------")
        # PARAMETER
        network = '213.0.184.0/24'
        # QUERY
        print(f"Parameter: {network}")
        try:
            ine = helper_ip_network.get(network)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        try:
            iaes = helper_ip_address.get_all_of_entity_network(ine)
        except DoesNotExist as e:
            self.fail(f"!!! {str(e)} !!!")
        result_dnes = set()
        for iae in iaes:
            try:
                dnes = helper_ip_address.resolve_reversed_access_path(iae, add_dne_along_the_chain=False)
            except (NoAvailablePathError, DoesNotExist) as exc:
                self.fail(f"!!! {str(exc)} !!!")
            for dne in dnes:
                result_dnes.add(dne)
        for i, dne in enumerate(result_dnes):
            print(f"domain name[{i+1}/{len(result_dnes)}]: {dne.string}")
        print(f"------- [2] END QUERY DOMAIN NAMES FROM NETWORK -------")


if __name__ == '__main__':
    unittest.main()
