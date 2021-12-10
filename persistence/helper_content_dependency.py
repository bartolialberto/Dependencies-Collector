from typing import List
from peewee import DoesNotExist
from entities.ContentDependenciesResolver import ContentDependencyEntry
from persistence.BaseModel import PageEntity, LandingPageEntity, ContentDependencyEntity, ContentDependencyAssociation


def multiple_inserts(result: dict) -> None:
    """
    This method executes multiple insert methods from the landing page resolving result (dictionary).

    :param result: The landing page resolving result.
    :type result: Dict[str, Tuple[str, List[ContentDependencyEntry], bool]]
    :raise peewee.DoesNotExist: If a landing page entity is not already present in the database.
    """
    for url in result.keys():
        try:
            insert(url, result[url])
        except DoesNotExist:
            raise


def insert(landing_page_url: str, entries: List[ContentDependencyEntry]) -> None:
    """
    This method inserts in the database of the application (DB) all the content dependencies associated with a landing
    page url. This method considers already persisted (in the database) the landing page entity otherwise it will
    raise an exception.

    :param landing_page_url: The landing page url.
    :type landing_page_url: str
    :param entries: List of content dependencies.
    :type entries: List[ContentDependencyEntry]
    :raise peewee.DoesNotExist: If the landing page entity is not already present in the database.
    """
    try:
        p = PageEntity.get(PageEntity.url == landing_page_url)
    except DoesNotExist:
        raise
    try:
        l = LandingPageEntity.get(LandingPageEntity.page == p.id)
    except DoesNotExist:
        raise
    for e in entries:
        try:
            cde = ContentDependencyEntity.get(ContentDependencyEntity.url == e.url, ContentDependencyEntity.mime_type == e.mime_type, ContentDependencyEntity.domain_name == e.domain_name, ContentDependencyEntity.state == e.response_code)
            ContentDependencyAssociation.get_or_create(landing_page=l, content_dependency_entity=cde)
        except DoesNotExist:
            cde = ContentDependencyEntity.create(url=e.url, mime_type=e.mime_type, state=e.response_code, domain_name=e.domain_name)
            ContentDependencyAssociation.get_or_create(landing_page=l, content_dependency_entity=cde)


def get_from_landing_page(landing_page_url: str) -> List[ContentDependencyEntry]:
    """
    Query that retrieves all the content dependencies present in the database related with a landing page url.
    This method considers already persisted (in the database) the landing page entity otherwise it will raise an
    exception.

    :param landing_page_url: An url.
    :type landing_page_url: str
    :raise DoesNotExist: If the landing page entity is not already present in the database.
    :return: Result of the query.
    :rtype: List[ContentDependencyEntry]
    """
    try:
        p = PageEntity.get(PageEntity.url == landing_page_url)
    except DoesNotExist:
        raise
    try:
        l = LandingPageEntity.get(LandingPageEntity.page == p)
    except DoesNotExist:
        raise
    query = ContentDependencyEntity.select()\
        .join(ContentDependencyAssociation)\
        .where(ContentDependencyAssociation.landing_page == l)
    result = list()
    for row in query:
        result.append(ContentDependencyEntry(row.domain_name, row.url, row.state, row.mime_type))
    return result
