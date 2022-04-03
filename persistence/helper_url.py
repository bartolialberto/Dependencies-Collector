from peewee import DoesNotExist
from entities.Url import Url
from persistence.BaseModel import UrlEntity


def insert(url: Url) -> UrlEntity:
    ue, created = UrlEntity.get_or_create(string=url.second_component())
    return ue


def get(url: Url) -> UrlEntity:
    try:
        return UrlEntity.get_by_id(url.second_component())
    except DoesNotExist:
        raise
