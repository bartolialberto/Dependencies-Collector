import unittest
from peewee import DoesNotExist
from exceptions.EmptyResultError import EmptyResultError
from persistence import helper_ip_range_tsv, helper_rov


class ASAndROVRelationQueryTestCase(unittest.TestCase):
    def test_1_get_ip_range_tsv_from_ip_address(self):
        """
        For each IP address the database should always have only one association (IpAddressDependsAssociation) with the
        other 3 entities: IpNetworkEntity, IpRangeTSVEntity, IpRangeROVEntity.
        This test performs a query that implicitly takes such constraint NOT for granted. So this test executes a query
        and at the same time checks for more than 1 IpAddressDependsAssociation for an IP address.

        """
        print(f"\n------- [1] START GETTING IP RANGE TSV FROM IP ADDRESS QUERY -------")
        # PARAMETER
        ip_address_string = '193.0.14.129'
        # QUERY
        try:
            irtes = helper_ip_range_tsv.get_all_from(ip_address_string)
        except (DoesNotExist, EmptyResultError) as e:
            self.fail(f"!!! {str(e)} !!!")
        for i, irte in enumerate(irtes):
            print(f"ip_range_tsv[{i+1}]: {str(irte)}")
        print(f"------- [1] END GETTING IP RANGE TSV FROM IP ADDRESS QUERY -------")

    def test_2_get_rov_from_ip_address(self):
        """
        For each IP address the database should always have only one association with the other 3 entities:
        IpNetworkEntity, IpRangeTSVEntity, IpRangeROVEntity.
        This test performs a query that implicitly takes such constraint NOT for granted. So this test executes a query
        and at the same time checks for more than 1 IpAddressDependsAssociation for an IP address.

        """
        print(f"\n------- [2] START GETTING ROV FROM IP ADDRESS QUERY -------")
        # PARAMETER
        ip_address_string = '193.0.14.129'
        # QUERY
        try:
            results = helper_rov.get_all_from(ip_address_string, with_ip_range_rov_string=True)
        except (DoesNotExist, EmptyResultError) as e:
            self.fail(f"!!! {str(e)} !!!")
        for i, tupl in enumerate(results):
            print(f"rov[{i+1}]: {str(tupl[0])} through ip_range_rov: {tupl[1]}")
        print(f"------- [2] END GETTING ROV FROM IP ADDRESS QUERY -------")


if __name__ == '__main__':
    unittest.main()
