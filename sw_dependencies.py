import selenium
from entities.FirefoxContentDependenciesResolver import FirefoxContentDependenciesResolver
from exceptions.GeckoDriverExecutableNotFoundError import GeckoDriverExecutableNotFoundError

path_firefox = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
domain = "www.youtube.it"

try:
    resolver = FirefoxContentDependenciesResolver()
    content_dependencies, domain_list = resolver.search_script_application_dependencies(domain)
    resolver.close()
    print(f"javascript/application dependencies found: {len(content_dependencies)} on {len(domain_list)} domains.")
except selenium.common.exceptions.WebDriverException as e1:
    print(f"!!! {str(e1)} !!!")
except GeckoDriverExecutableNotFoundError as e2:
    print(f"!!! {e2.message} !!!")

print("THE END")