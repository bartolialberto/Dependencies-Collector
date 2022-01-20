import unittest
from persistence import helper_application_results
from persistence.BaseModel import IpAddressDependsAssociation, AutonomousSystemEntity, WebSiteEntity, ScriptSiteEntity, \
    NameServerEntity, PrefixesTableAssociation


class DumpUnresolvedEntitiesQueryTestCase(unittest.TestCase):
    def test_getting_unresolved_entities(self):
        results = helper_application_results.dump_unresolved_entities()
        for i, res in enumerate(results):
            if isinstance(res, IpAddressDependsAssociation):
                print(f"[{i+1}/{len(results)}]: IpAddressDependsAssociation = {str(res)}")
            elif isinstance(res, PrefixesTableAssociation):
                print(f"[{i + 1}/{len(results)}]: PrefixesTableAssociation = {str(res)} from IpAddressEntity = {str(res)}")
            elif isinstance(res, WebSiteEntity):
                print(f"[{i + 1}/{len(results)}]: WebSiteEntity = {str(res)}")
            elif isinstance(res, ScriptSiteEntity):
                print(f"[{i + 1}/{len(results)}]: ScriptSiteEntity = {str(res)}")
            elif isinstance(res, NameServerEntity):
                print(f"[{i + 1}/{len(results)}]: NameServerEntity = {str(res)}")
            else:
                print(f"[{i + 1}/{len(results)}]: ??? = ???")


if __name__ == '__main__':
    unittest.main()
