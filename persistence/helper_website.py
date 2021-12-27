from peewee import DoesNotExist
from persistence import helper_url
from persistence.BaseModel import WebSiteEntity
from utils import url_utils


def insert(url: str) -> WebSiteEntity:
    ue = helper_url.insert(url)
    we, created = WebSiteEntity.get_or_create(url=ue)
    return we


def get(url: str) -> WebSiteEntity:
    temp = url_utils.deduct_second_component(url)
    try:
        ue = helper_url.get(temp)
    except DoesNotExist:
        raise
    try:
        return WebSiteEntity.get(WebSiteEntity.url == ue)
    except DoesNotExist:
        raise
