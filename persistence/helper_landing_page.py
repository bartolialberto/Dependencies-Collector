from typing import List, Tuple, Dict
from persistence.BaseModel import PageEntity, LandingPageEntity, RedirectionPath, LandsAssociation, DomainNameEntity


def multiple_inserts(landing_page_results: dict):
    for domain_name in landing_page_results.keys():
        insert(domain_name,
               landing_page_results[domain_name][0],
               landing_page_results[domain_name][1],
               landing_page_results[domain_name][2])


def insert(domain_name: str, landing_url: str, redirection_path: List[str], hsts: bool):
    la_p, created = PageEntity.get_or_create(url=landing_url, hsts=hsts)
    lp, created = LandingPageEntity.get_or_create(page=la_p)
    for page in redirection_path:
        p, created = PageEntity.get_or_create(url=page, hsts=hsts)
        RedirectionPath.get_or_create(landing_page=lp.page, page=p)
    query = DomainNameEntity.select().where(DomainNameEntity.name == domain_name)
    for row in query:
        LandsAssociation.get_or_create(domain_name=row, landing_page=lp)
        break       # first occurrence


# FIXME: doesn't work
def get_from_domain_name(domain_name: str) -> Tuple[str, List[str], bool]:      # da testare e mettere a posto
    query = LandsAssociation.select()\
        .join_from(LandsAssociation, DomainNameEntity)\
        .join_from(LandsAssociation, LandingPageEntity)\
        .where(DomainNameEntity.name == domain_name)
    landing_page = None
    for row in query:
        landing_page = row.landing_page
        #q = RedirectionPath.select().where(RedirectionPath.landing_page_id == landing_page.id)
        #q = RedirectionPath.select().join_from(RedirectionPath, PageEntity, on=(RedirectionPath.landing_page_id == landing_page.id)) #.where(RedirectionPath.landing_page_id == landing_page.id)
        q = RedirectionPath.select()\
            .join_from(RedirectionPath, LandingPageEntity)\
            .where(RedirectionPath.landing_page_id == landing_page.id)
        for r in q:
            print(r.page_id)
        redirection_path = list()
        hsts = False
        for r in q:
            print(r.page.url)
            redirection_path.append(r.page.url)
            hsts = r.page.hsts
        return landing_page, redirection_path, hsts
