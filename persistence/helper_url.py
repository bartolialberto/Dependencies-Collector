from peewee import DoesNotExist
from exceptions.InvalidUrlError import InvalidUrlError
from persistence.BaseModel import UrlEntity
from utils import url_utils


def insert(string: str) -> UrlEntity:
    try:
        url = url_utils.deduct_second_component(string)
    except InvalidUrlError:
        raise
    ue, created = UrlEntity.get_or_create(string=url)
    return ue


def get(url: str) -> UrlEntity:
    try:
        return UrlEntity.get_by_id(url)
    except DoesNotExist:
        raise

