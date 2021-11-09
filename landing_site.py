import requests
from entities.LandingSiteHttpsResolver import LandingSiteHttpsResolver
from entities.LandingSiteHttpResolver import LandingSiteHttpResolver


domain = "www.darklyrics.com"
print(f"Trying to connect to domain '{domain}' via https:")
try:
    landing_site_resolver = LandingSiteHttpsResolver(domain)
    print(f"Landing url: {landing_site_resolver.landing_url}\nLanding domain: {landing_site_resolver.landing_domain}")
    print(f"Redirection path:")
    for index, url in enumerate(landing_site_resolver.redirection_path):
        print(f"[{index + 1}/{len(landing_site_resolver.redirection_path)}]: {url}")
    print(f"Is there a domain redirection? {landing_site_resolver.domain_redirection}")
except requests.exceptions.ConnectionError as e:
    try:
        print(f"Seems that https is not supported.")
        print(f"Trying to connect to domain '{domain}' via http:")
        landing_site_resolver = LandingSiteHttpResolver(domain)
        print(f"Landing url: {landing_site_resolver.landing_url}\nLanding domain: {landing_site_resolver.landing_domain}")
        print(f"Redirection path:")
        for index, url in enumerate(landing_site_resolver.redirection_path):
            print(f"[{index + 1}/{len(landing_site_resolver.redirection_path)}]: {url}")
        print(f"Is there a domain redirection? {landing_site_resolver.domain_redirection}")
    except Exception as e:
        print(f"!!! {str(e)} !!!")
except Exception as e:
    print(f"!!! {str(e)} !!!")
print("THE END")
