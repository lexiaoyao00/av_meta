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
from typing import List,Dict
import re



class Jav321Spider(AsyncBaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = URL('https://www.jav321.com')
        self.cookies = {
            'UGVyc2lzdFN0b3JhZ2U': '%7B%7D',
            '_ga': 'GA1.2.1119708300.1768562730',
            '__PPU_puid': '7515763464587527403',
            'is_loyal': '1',
            '_gid': 'GA1.2.1546455009.1771993760',
            '_gat': '1',
            '_ga_EHB905C35N': 'GS2.2.s1771993760$o7$g1$t1771993933$j34$l0$h0',
        }

        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.jav321.com',
            'priority': 'u=0, i',
            'referer': 'https://www.jav321.com/search',
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


    def _parse(self,url:str, r:Response):
        selector  = Selector(r.text)

        info_sel = selector.xpath('//div[@class="panel panel-info"][1]')
        # --- 简介 ---
        title = info_sel.css('div.panel-heading h3::text').get()
        if not title:
            logger.error('无法获取标题')
            return None
        title = title.strip()

        # --- 信息拆分 ---
        info_div = info_sel.css('div.col-md-9').get()
        inner_html : str = re.sub(r'^<div.*?>|</div>$', '', info_div, flags=re.DOTALL)
        lines = inner_html.split('<br>')
        panel_info_lines : Dict[str, str] = {}

        for line in lines:
            # 2. 将每一行 HTML 片段转换成纯文本
            # 使用 Selector(text=line).xpath('string(.)') 可以直接去掉所有 HTML 标签，只留文字
            text_content = Selector(text=line).xpath('string(.)').get()

            if not text_content or ':' not in text_content:
                continue

            # 3. 按照第一个出现的冒号 : 分割 Key 和 Value
            # 使用 split(':', 1) 保证只切分第一个冒号，防止 Value 里也带冒号导致切分过多
            key, value = text_content.split(':', 1)

            key = key.strip()
            value = value.strip().replace('\xa0', '') # 清理空格和 &nbsp;

            panel_info_lines[key] = value


        num_code = panel_info_lines.get('品番')
        if not num_code:
            logger.error('无法获取番号')
            return None

        series = panel_info_lines.get('シリーズ')
        movie_info_meta = NfoMovieModel(num_code=num_code, website=url, title=title,set=series)

        releasedate  = panel_info_lines.get('配信開始日')    # 上映日期

        movie_info_meta.releasedate = releasedate

        # --- 简介 ---
        plot = info_sel.xpath('//div[@class="panel-body"]/div[@class="row"]/div[@class="col-md-12"][last()]/text()').get()
        introduction_meta = NfoMovieIntroductionModel(plot=plot)
        movie_info_meta.introduction_meta = introduction_meta


        # --- 演员 ---
        actors_str = panel_info_lines.get('出演者')
        if actors_str:
            actors = actors_str.split(' ')
            actors_meta = [NfoActorModel(name=actor) for actor in actors]
            movie_info_meta.actors = actors_meta

        # --- 制作团队 ---

        studio = panel_info_lines.get('メーカー')

        production_meta = NfoMovieProductionModel(studio=studio)
        movie_info_meta.production_meta = production_meta

        # --- 评分 ---

        rating = panel_info_lines.get('平均評価')
        if rating:
            rating = float(rating)
            movie_info_meta.rating = rating

        # --- 标签 ---

        genres = panel_info_lines.get('ジャンル')
        if genres:
            genres = genres.split(' ')
            tag_meta = NfoMovieTagModel(genre=genres)
            movie_info_meta.tag_meta = tag_meta


        # --- 图像 ---

        poster = info_sel.css('div.panel-body div.col-md-3 img::attr(src)').get()
        thumb = info_sel.css('div.col-md-12 video#vjs_sample_player::attr(poster)').get()
        extrafanart = selector.xpath('//body/div[@class="row"][2]/div[@class="col-md-3"]//p/a/img/@src').getall()
        imgs_meta = NfoMovieImageModel(poster=poster, extrafanart=extrafanart, thumb=thumb)
        movie_info_meta.imgs_meta = imgs_meta

        return movie_info_meta



    async def search(self, num_code:str):
        # 直接访问会加载不出来封面
        # num_code_r =  num_code.replace('-', '00')
        # search_url = self.base_url / 'video' / num_code_r
        search_url = self.base_url / 'search'
        data = {
            'sn': num_code
        }
        search_url = search_url.with_query(data)
        response = await self.post(str(search_url), headers = self.headers, cookies = self.headers, data=data)
        if response is None:
            logger.error(f'jav321 搜索 {num_code} 失败')
            return None

        movie_info_meta = self._parse(str(search_url),response)
        if movie_info_meta is None:
            logger.error(f'jav321 解析 {num_code} 失败')
            return None

        return movie_info_meta
