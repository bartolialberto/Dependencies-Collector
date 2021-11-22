from typing import List
from entities.ContentDependenciesResolver import ContentDependencyEntry
from persistence.BaseModel import LandingPageEntity, PageEntity, ContentDependencyEntity, ContentDependencyAssociation


def multiple_inserts(results: dict) -> None:
    for url in results.keys():
        insert(url, results[url])


def insert(landing_page_url: str, entries: List[ContentDependencyEntry]) -> None:
    p = PageEntity.get(url=landing_page_url)
    l = LandingPageEntity.get(LandingPageEntity.page == p.id)
    for e in entries:
        cde, create = ContentDependencyEntity.get_or_create(url=e.url, mime_type=e.mime_type, state=e.response_code, domain_name=e.domain_name)
        ContentDependencyAssociation.get_or_create(landing_page=l, content_dependency_entity=cde)


def get_from_landing_page(landing_page_url: str) -> List[ContentDependencyEntry]:
    p = PageEntity.get(PageEntity.url == landing_page_url)
    l = LandingPageEntity.get(LandingPageEntity.page == p)
    query = ContentDependencyEntity.select()\
        .join(ContentDependencyAssociation)\
        .where(ContentDependencyAssociation.landing_page == l)
    result = list()
    for row in query:
        result.append(ContentDependencyEntry('da togliere?', row.url, row.state, row.mime_type))
    return result
