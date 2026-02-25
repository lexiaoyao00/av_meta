__all__ = [
    'Jav321Spider',
    'JavBusSpider',
]

from .jav321 import Jav321Spider
from .javbus import JavBusSpider

from typing import Dict,Type
from core.crawler_async import AsyncBaseCrawler


spider_type_dict : Dict[str, Type[AsyncBaseCrawler]] = {
    'jav321': Jav321Spider,
    'javbus': JavBusSpider,
}