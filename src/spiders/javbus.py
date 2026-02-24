from core.crawler_async import AsyncBaseCrawler
from schemas.movie import (
    NfoActorModel,
    NfoMovieImageModel,
    NfoMovieTagModel,
    NfoMovieProductionModel,
    NfoMovieIntroductionModel,
    NfoMovieModel)
from parsel import Selector
from curl_cffi import Response
from loguru import logger
from yarl import URL
from typing import List


javbus_cookies = {
    'existmag': 'mag',
    'PHPSESSID': 'bv30trfu2405r7e8scnlukrh05',
    '4fJN_2132_saltkey': 'tfyoLLKy',
    '4fJN_2132_lastvisit': '1771895547',
    '4fJN_2132_sid': 'JLLFXr',
    '4fJN_2132_seccodecSJLLFXr': '3468.c0ba0bbad7ca07295a',
    '4fJN_2132_ulastactivity': 'b44cDl0C5wQFITtD5%2BWU1L4XaxsgzYnBpOjy5sLs%2B2QjRRNJplDq',
    '4fJN_2132_creditnotice': '0D1D1D0D0D0D0D0D0D404293',
    '4fJN_2132_creditbase': '0D8D8D0D0D0D0D0D0',
    '4fJN_2132_creditrule': '%E6%AF%8F%E5%A4%A9%E7%99%BB%E9%8C%84',
    '4fJN_2132_lastcheckfeed': '404293%7C1771899157',
    '4fJN_2132_lastact': '1771899167%09uc.php%09',
    '4fJN_2132_auth': 'b625%2BKWlO8xJu5qTT8wSIBd5W4y52xjjzyqGQ2A%2Fxta0Kuoq0itIEm79YxVCTdNVoEZw8NtDLiRRVwUdLLQb4RGmUAY',
    'bus_auth': '6ebe1%2FSIieLvxC8Zhf%2FiVLumoyFA%2FVwigD75v0JJjkd%2FM8ZpkkBvS%2FbgHZi0',
}

javbus_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
}


class JavBusSpider(AsyncBaseCrawler):
    def __init__(self):
        self.base_url = URL('https://www.javbus.com')
        super().__init__()

    def _parse(self,url:str, response : Response):
        selector  = Selector(response.text)

        # 类别，无码还是有码
        censored_or_unce = selector.css('div#navbar ul.nav.navbar-nav li.active a::text').get()
        if censored_or_unce == '有碼':
            poster_path = 'thumb'
        elif censored_or_unce == '無碼':
            poster_path = 'thumbs'
        else:
            logger.error('javbus 未知的影片马赛克类别')
            raise Exception('javbus 未知的影片马赛克类别')

        # --- 简介 ---
        tilte = selector.css('h3::text').get()

        # --- 制作团队 ---
        move_info_sel = selector.css('div.row.movie div.info')
        info_list = move_info_sel.xpath('./p[not(@class)]').xpath('normalize-space(.)').getall()

        info_dict = {}
        for info in info_list:
            seq_list = info.split(':',1)
            if len(seq_list) == 2:
                info_dict[seq_list[0]] = seq_list[1].strip()

        code = info_dict.get('識別碼')
        releasedate = info_dict.get('發行日期')
        series = info_dict.get('系列')      # 合集 set

        director = info_dict.get('導演')
        studio = info_dict.get('製作商')
        publisher = info_dict.get('發行商')


        movie_production = NfoMovieProductionModel(director=director,studio=studio,publisher=publisher)

        # --- 图像 ---
        bigImage = selector.css('a.bigImage::attr(href)').get().strip('/')
        thumb = str(self.base_url / bigImage)
        poster = thumb.replace('cover',poster_path).replace('_b','')
        # print(f'poster = {poster}')
        # print(f'thumb = {thumb}')

        fanarts = selector.css('div#sample-waterfall a.sample-box::attr(href)').getall()
        # print(f'fanarts = {fanarts}')

        movie_images = NfoMovieImageModel(poster=poster,thumb=thumb,fanart=fanarts)

        # --- 标签 ---
        genres = move_info_sel.css('p > span.genre > label > a::text').getall()

        # print(genres)

        move_tags = NfoMovieTagModel(genre=genres)

        # --- 演员 ---
        actors = move_info_sel.css('p > span.genre > a::text').getall()

        # print(actors)
        actor_info : List[NfoActorModel] = [NfoActorModel(name=actor) for actor in actors]
        # print(actor_info)

        movie_meta = NfoMovieModel(
            num_code=code,
            website=url,
            title=tilte,
            releasedate=releasedate,
            set=series,
            actors=actor_info,
            production_meta=movie_production,
            tag_meta=move_tags,
            imgs_meta=movie_images,
            )

        return movie_meta

    async def search(self, num_code : str):
        search_url = f'https://www.javbus.com/{num_code}'
        response = await self.get(search_url,headers=javbus_headers, cookies=javbus_cookies)
        movie_info_meta = self._parse(search_url,response)
        movie_info_meta.save_to_nfo(f'{num_code}.nfo')

    # async def test(self):
    #     test_url = 'https://www.javbus.com/mide-565'
    #     response = await self.get(test_url,headers=javbus_headers, cookies=javbus_cookies)
    #     self._parse(response)
