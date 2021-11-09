from utils import domain_name_utils


url = "https://www.darklyrics.com"
result = domain_name_utils.deduct_domain_name(url)
print(f"{url} -> {result}")

url = "https://www.darklyrics.com/"
result = domain_name_utils.deduct_domain_name(url)
print(f"{url} -> {result}")

url = "https://darklyrics.com"
result = domain_name_utils.deduct_domain_name(url)
print(f"{url} -> {result}")

url = "https://darklyrics.com/"
result = domain_name_utils.deduct_domain_name(url)
print(f"{url} -> {result}")

domain = "www.darklyrics.com."
result = domain_name_utils.deduct_url(domain)
print(f"{domain} -> {result}")

domain = "darklyrics.com."
result = domain_name_utils.deduct_url(domain)
print(f"{domain} -> {result}")

domain = "www.darklyrics.com"
result = domain_name_utils.deduct_url(domain)
print(f"{domain} -> {result}")

domain = "darklyrics.com"
result = domain_name_utils.deduct_url(domain)
print(f"{domain} -> {result}")
print("THE END")
