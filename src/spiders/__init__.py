__all__ = [
    'Jav321Spider',
    'JavBusSpider',
    'JavDBSpider',
]

from .jav321 import Jav321Spider
from .javbus import JavBusSpider
from .javdb import JavDBSpider
from .missav import MissavSpider

from typing import Dict,Type
from core.crawler_async import AsyncBaseCrawler


SPIDER_TYPE_MAP : Dict[str, Type[AsyncBaseCrawler]] = {
    'javdb' : JavDBSpider,
    'javbus': JavBusSpider,
    'jav321': Jav321Spider,
}