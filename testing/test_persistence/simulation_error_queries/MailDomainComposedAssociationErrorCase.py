import unittest
from peewee import DoesNotExist
from entities.DomainName import DomainName
from persistence import helper_mail_domain, helper_mail_domain_composed


class MailDomainComposedAssociationErrorCase(unittest.TestCase):
    def test_01_set_mail_domain_composed_to_null(self):
        print(f"\n------- [1] START SETTING MAIL DOMAIN COMPOSED ASSOCIATION TO NULL QUERY -------")
        # PARAMETERS
        for_mail_domain = DomainName('pec.comune.gardonevaltrompia.bs.it.')
        # ELABORATION
        print(f"Domain name: {for_mail_domain}")
        try:
            mde = helper_mail_domain.get(for_mail_domain)
            mdcas = helper_mail_domain_composed.get_of_entity_mail_domain(mde)
            for mdca in mdcas:
                    mdca.delete_instance()
        except DoesNotExist:
            mde = helper_mail_domain.insert(for_mail_domain)
        helper_mail_domain_composed.insert(mde, None)
        print(f"------- [1] END SETTING MAIL DOMAIN COMPOSED ASSOCIATION TO NULL QUERY -------")


if __name__ == '__main__':
    unittest.main()
