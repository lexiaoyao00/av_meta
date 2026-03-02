from core.crawler_async import AsyncBaseCrawler
from schemas import (
    NfoActorModel,
    NfoMovieImageModel,
    NfoMovieTagModel,
    NfoMovieProductionModel,
    NfoMovieIntroductionModel,
    NfoMovieSetModel,
    NfoMovieModel)
from parsel import Selector
from curl_cffi import Response
from loguru import logger
from yarl import URL
from typing import List,Dict
import re


class MissavSpider(AsyncBaseCrawler):
    def __init__(self):
        ...


    async def search(self, num_code:str):
        ...