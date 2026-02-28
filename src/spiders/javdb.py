from core.crawler_async import AsyncBaseCrawler
from schemas.movie import (
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


class JavDBSpider(AsyncBaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = URL('https://javdb.com')
        self.cookies = {
            'list_mode': 'h',
            'theme': 'auto',
            'locale': 'zh',
            'over18': '1',
            '_ym_uid': '1768809557562265717',
            '_ym_d': '1768809557',
            'cf_clearance': 'kRrXqMBK84_RsAyoVgMZ9UivRkekP7xL4.af4zVbJsg-1772256267-1.2.1.1-0Z2_.ab0W2fThKvPiADGt.GY6klGAHgA75RcKHK4AssjPVXV0x.9XD3siv4qz4lFoqe4ZpXrxwzsGONhdA5ANdm.NXXQNjdyuk7xDscBo4WgFqlEj90sAyEgGMr136xD_cL8ddY2pXJYNZsKgvjP65R.QRfInBqD46yztypFFXp.TbQNurd1RYonM4TH7NVc7GRZV7utqTOM.W5fdtpFYfA7B5jTt4xbKHpLhWxso.c',
            '_ym_isad': '2',
            '_jdb_session': 'ec2Rtvb9XNnaUb4RVOOZGPBxznW4%2BjLTYOuyOTvEqDGw2nVmG9xMQVStCMnH9E84b%2FBOyJop984eD2Ju25AqKmuDeCiMGMBgCqo2%2BwKBTjjIAsCH%2F9MPA4ir5HyWCthzu9jL04VUWOBM3K7wccgson006U%2FNlOqPceBeNLfn7%2BaeFhNtILrhQM9D%2F5Yl%2BBXelnQpO1CGZyngyavdgLsD8KoJnkCaY0dwaAgKv0UrXrzgVrO7sj3oCmpAPgfSmb%2F7W%2FHhuB8i0X0rwZvjyoODJS0T46AtVHiZMe9VxC4yQ5gTlcxrLrdPj1%2F9lky5wXh7nI%2B9ZpopwGV5jeTAyTG3RF%2B8EbyOINAm2C%2FhLUubGM3DCGL1PaojR7mNtO4IMvctyUc%3D--Xusaq7rzAATyMnDD--8b4AkFaHenDPY8LbBKN1Pw%3D%3D',
        }

        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'referer': 'https://javdb.com/',
            'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
        }


    async def search(self, num_code : str):
        # return super().search(num_code)
        search_url = self.base_url / 'search'
        search_params = {
            'q': num_code,
        }
        search_response : Response = await self.get(str(search_url),
                                  params=search_params,
                                  cookies=self.cookies,
                                  headers=self.headers)

        if search_response is None:
            logger.error(f'javdb 搜索 {num_code} 失败')
            return None

        movie_url = self._parse_search_rsp(num_code, search_response)

        if movie_url is None:
            logger.error(f'javdb 获取 {num_code} 影片链接失败')
            return None

        movie_response : Response = await self.get(str(movie_url),
                                  cookies=self.cookies,
                                  headers=self.headers)

        if movie_response is None:
            logger.error(f'javdb 访问 {num_code} 影片页面失败')
            return None

        movie_info_meta = self._parse_movie_rsp(str(movie_url), movie_response)
        if movie_info_meta is None:
            logger.error(f'javdb 解析 {num_code} 影片元数据失败')
            return None

        return movie_info_meta


    def _parse_search_rsp(self,num_code:str, rsp:Response):
        if rsp is None:
            return None
        num_code = num_code.lower().strip()
        sel = Selector(rsp.text)
        search_items_sel = sel.css('div.movie-list > div.item')
        for search_item_sel in search_items_sel:
            title_num_code = search_item_sel.css('div.video-title > strong::text').get().lower().strip()
            if title_num_code == num_code:
                if (href := search_item_sel.css('a.box::attr(href)').get()) is None:
                    continue
                movie_url = self.base_url / href.strip('/')
                return movie_url

        return None

    def _parse_movie_rsp(self,url:str, rsp: Response) -> NfoMovieModel | None:
        if rsp is None:
            return None
        sel = Selector(rsp.text)
        num_code = sel.css('nav.movie-panel-info div.panel-block.first-block span.value').xpath('normalize-space(.)').get()
        movie = NfoMovieModel(num_code=num_code,website=url)
        title = sel.css('span.origin-title::text').get()
        if title is None:
            title = sel.css('strong.current-title::text').get()
            if title is None:
                logger.error('javdb 未找到识别码')
                return None

        movie.title = title
        # movie_info = movie.model_dump(exclude_none=True)
        # logger.debug(f'javdb 解析 {movie_info}')
        panel_list = sel.css('nav.movie-panel-info div.panel-block').xpath('normalize-space(.)').getall()
        info_dict : Dict[str,str]= {}
        for panel in panel_list:
            info_pair = panel.split(':',1)
            if len(info_pair) != 2:
                continue
            info_dict[info_pair[0].strip()] = info_pair[1].strip()


        # [番號 , 日期, 時長, 導演, 片商, 發行, 評分, 系列, 類別, 演員]
        # print(info_dict)
        #  ------- 制作团队 -------
        director = info_dict.get('導演')        #导演

        studio = info_dict.get('片商')            #片商
        publisher = info_dict.get('發行')            #发行
        movie.production_meta = NfoMovieProductionModel(director=director,studio=studio,publisher=publisher)

        # ------- 评分 -------
        rating_str = info_dict.get('評分',"")            #评分
        if (rating_match := re.search(r'(\d+\.?\d*)分', rating_str)):
            rating = float(rating_match.group(1))
            movie.rating = rating

        # ------- 日期 -------
        releasedate = info_dict.get('日期')            #日期
        if releasedate is not None:
            movie.releasedate = releasedate

        # 系列
        series = info_dict.get('系列')            #系列
        if series is not None:
            movie.set = NfoMovieSetModel(name=series)

        # ------- 類別 -------
        genre_list = info_dict.get('類別').split(',')            #类别
        genres = [genre.strip() for genre in genre_list]
        movie.tag_meta = NfoMovieTagModel(genre=genres)


        # ------- 演员 -------
        actors_str = info_dict.get('演員')            #演员
        if actors_str:
            actors = actors_str.split(f'\xa0 ')
            movie.actors = []
            for actor in actors:
                if '♀' in actor:
                    actor = actor.replace('♀','')
                    movie.actors.append(NfoActorModel(name=actor,role='女优'))
                # NfoMovieActorModel(name=actor)
                if '♂' in actor:
                    actor = actor.replace('♂','')
                    movie.actors.append(NfoActorModel(name=actor,role='男优'))


        # ------- 封面 剧照 -------
        img_meta = NfoMovieImageModel()
        cover_url = sel.css('img.video-cover::attr(src)').get()
        if cover_url:
            img_meta.poster = cover_url
            img_meta.thumb = cover_url

        pre_imgs = sel.css('div.tile-images.preview-images a.tile-item::attr(href)').getall()
        if pre_imgs:
            img_meta.extrafanart = pre_imgs

        movie.imgs_meta = img_meta


        return movie

