__all__ = [
    'Jav123Spider',
    'JavBusSpider',
]

from .jav123 import Jav123Spider
from .javbus import JavBusSpider

from typing import Dict,Type
from core.crawler_async import AsyncBaseCrawler


spider_type_dict : Dict[str, Type[AsyncBaseCrawler]] = {
    'jav123': Jav123Spider,
    'javbus': JavBusSpider,
}