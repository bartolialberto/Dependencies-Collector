import unittest
from peewee import DoesNotExist
from persistence import helper_mail_server, helper_mail_domain


class MailServerDependenciesQueryTestCase(unittest.TestCase):
    def test_1_get_mail_servers_of_mail_domain(self):
        print(f"\n------- [1] START GETTING DEPENDENCIES OF MAIL DOMAIN QUERY -------")
        # PARAMETER
        mail_domain = 'pec.it.'
        # QUERY
        try:
            mses = helper_mail_server.get_every_of(mail_domain)
        except DoesNotExist as e:
            self.fail(str(e))
        print(f"Parameter: {mail_domain}")
        print(f"Mail server dependencies of mail domain: {mail_domain}")
        for i, mse in enumerate(mses):
            print(f"mail_server[{i+1}/{len(mses)}] = {mse.name.string}")
        print(f"------- [1] END GETTING DEPENDENCIES OF MAIL DOMAIN QUERY -------")

    def test_1_get_mail_domains_from_mail_server(self):
        print(f"\n------- [2] START GETTING MAIL DOMAINS FROM MAIL SERVERS QUERY -------")
        # PARAMETER
        mail_server = 'alt1.gmail-smtp-in.l.google.com.'
        # QUERY
        try:
            mdes = helper_mail_domain.get_every_of(mail_server)
        except DoesNotExist as e:
            self.fail(str(e))
        print(f"Parameter: {mail_server}")
        for i, mde in enumerate(mdes):
            print(f"mail_domain[{i+1}/{len(mdes)}] = {mde.name.string}")
        print(f"------- [2] END GETTING MAIL DOMAINS FROM MAIL SERVERS QUERY -------")


if __name__ == '__main__':
    unittest.main()
