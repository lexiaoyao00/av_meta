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


spider_type_dict : Dict[str, Type[AsyncBaseCrawler]] = {
    'javdb' : JavDBSpider,
    'jav321': Jav321Spider,
    'javbus': JavBusSpider,
}