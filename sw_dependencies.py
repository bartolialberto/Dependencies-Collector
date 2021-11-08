from entities.FirefoxContentDependenciesResolver import FirefoxContentDependenciesResolver


path_firefox = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe'
# path_geckodriver = 'C:\\Users\\fabbi\\PycharmProjects\\LavoroTesi\\input\\geckodriver.exe'
path_geckodriver = "input/geckodriver.exe"
domain = "www.youtube.it"

resolver = FirefoxContentDependenciesResolver()
content_dependencies, domain_list = resolver.search_dependencies(domain)
resolver.close()

print("THE END")