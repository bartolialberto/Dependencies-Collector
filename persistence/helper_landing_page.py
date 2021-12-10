from typing import List, Tuple
from peewee import DoesNotExist
from persistence.BaseModel import PageEntity, LandingPageEntity, RedirectionPathAssociation, DomainNameEntity, \
    LandsAssociation


def multiple_inserts(landing_page_results: dict):
    """
    This method executes multiple insert methods from the landing page resolving result (dictionary).

    :param landing_page_results: The landing page resolving result.
    :type landing_page_results: Dict[str, List[str], bool]
    """
    for domain_name in landing_page_results.keys():
        insert(domain_name,
               landing_page_results[domain_name][0],
               landing_page_results[domain_name][1],
               landing_page_results[domain_name][2])


def insert(domain_name: str, landing_url: str, redirection_path: List[str], hsts: bool):
    """
    This method inserts in the database of the application (DB) the landing page parameters
    of a single elaboration.

    :param domain_name: A domain name.
    :type domain_name: str
    :param landing_url: The landing page url.
    :type landing_url: str
    :param redirection_path: The redirection path.
    :type redirection_path: List[str]
    :param hsts: The strict-transport-security presence in the landing page.
    :type hsts: bool
    """
    la_p, created = PageEntity.get_or_create(url=landing_url, hsts=hsts)
    lp, created = LandingPageEntity.get_or_create(page=la_p.id)
    for page in redirection_path:
        p, created = PageEntity.get_or_create(url=page, hsts=hsts)
        RedirectionPathAssociation.get_or_create(landing_page=lp.id, page=p.id)
    dn, created = DomainNameEntity.get_or_create(name=domain_name)
    LandsAssociation.get_or_create(domain_name=dn, landing_page=lp)


def get_from_domain_name(domain_name: str) -> Tuple[str, List[str], bool]:
    """
    Query that retrieves all the landing page entities present in the database related to the landing page of the
    domain name parameter.
    This method needs that the domain name (parameter) and the landing page url (not a parameter) is already persisted
    in the database, otherwise an exception is raised.

    :param domain_name: A domain name.
    :type domain_name: str
    :raise: If the corresponding entity of the domain name or the landing page url is not found.
    :return: The tuple associated with the landing page associated with the domain name parameter.
    :rtype: Tuple[str, List[str], bool]
    """
    try:
        dne = DomainNameEntity.get(DomainNameEntity.name == domain_name)
    except DoesNotExist:
        raise
    query = LandsAssociation.select()\
        .join_from(LandsAssociation, LandingPageEntity)\
        .where(LandsAssociation.domain_name_id == dne.id)
    for row in query:
        return get_from_url(row.landing_page.page.url)


# TODO: ogni tanto testarlo per sicurezza
def get_from_url(url: str) -> Tuple[str, List[str], bool]:
    """
    Query that retrieves all the landing page entities present in the database related to a specific url.
    This method needs that the url parameter is already persisted in the database, otherwise an exception is raised.

    :param url: The url of a landing page.
    :type url: str
    :raise: If the corresponding entity of the url is not found.
    :return: The tuple associated with the landing page elaboration associated with the landing page url.
    :rtype: Tuple[str, List[str], bool]
    """
    try:
        pe = PageEntity.get(PageEntity.url == url)
    except DoesNotExist:
        raise
    try:
        lpe = LandingPageEntity.get(LandingPageEntity.page == pe.id)
    except DoesNotExist:
        raise
    redirection_path = list()
    hsts = False
    query = RedirectionPathAssociation.select()\
        .where(RedirectionPathAssociation.landing_page_id == lpe.id)
    for row in query:
        p = PageEntity.get_by_id(row.page_id)
        redirection_path.append(p.url)
        hsts = p.hsts
    return lpe.page.url, redirection_path, hsts
