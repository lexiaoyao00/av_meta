from schemas.movie import (
    NfoActorModel,
    NfoMovieImageModel,
    NfoMovieTagModel,
    NfoMovieProductionModel,
    NfoMovieIntroductionModel,
    NfoMovieModel)
from core.downloader import Downloader
from pathlib import Path
from config import settings
import shutil
from loguru import logger
from typing import List
import asyncio

class Organize:
    """整理文件并保存nfo文件"""
    def __init__(self, moive_info : NfoMovieModel, file_path : str|Path):
        """传入的 moive_info 是爬虫爬取到的元数据,修改后的元数据传入可能会报错"""
        self.moive_info = moive_info
        self.orgin_file = Path(file_path)
        # TODO:整理后的文件路径根据配置来
        self.organized_file = Path(settings.select_dir) / settings.output_dir / self.orgin_file.name


    def _download_imgs(self):
        """下载图片,包括剧照,封面等等
            下载后将对应的元数据修改为本地文件名
        """
        if self.moive_info.imgs_meta is None:
            return

        av_code = self.moive_info.num_code
        imgs_meta : NfoMovieImageModel = self.moive_info.imgs_meta
        downloader = Downloader()
        organized_dir = self.organized_file.parent

        if imgs_meta.poster is not None:
            self._donwload_poster(imgs_meta,av_code,downloader,organized_dir)

        if imgs_meta.thumb is not None:
            self._download_thumb(imgs_meta,av_code,downloader,organized_dir)

        if imgs_meta.fanart is not None:
            self._download_fanart(imgs_meta,av_code,downloader,organized_dir)

        self.moive_info.imgs_meta = imgs_meta


    def _donwload_poster(
            self,
            imgs_meta : NfoMovieImageModel,
            av_code : str,
            downloader : Downloader,
            organized_dir : Path):
        """下载封面"""
        suffix = imgs_meta.poster.split('.')[-1]
        save_file = f'{av_code}-poster.{suffix}'
        save_path = organized_dir / save_file
        asyncio.create_task(downloader.download_async(imgs_meta.poster, save_path))
        new_poster = save_path.stem
        imgs_meta.poster = new_poster

    def _download_thumb(
            self,
            imgs_meta : NfoMovieImageModel,
            av_code : str,
            downloader : Downloader,
            organized_dir : Path):
        """下载缩略图"""
        suffix = imgs_meta.thumb.split('.')[-1]
        save_file = f'{av_code}-thumb.{suffix}'
        save_path = organized_dir / save_file
        asyncio.create_task(downloader.download_async(imgs_meta.thumb, save_path))
        new_thumb = save_path.stem
        imgs_meta.thumb = new_thumb

    def _download_fanart(
            self,
            imgs_meta : NfoMovieImageModel,
            av_code : str,
            downloader : Downloader,
            organized_dir : Path):
        """下载剧照,保存到 extrafanart 中"""
        counter = 1
        new_fanart : List[str] = []
        for fanart_img in imgs_meta.fanart:
            suffix = fanart_img.split('.')[-1]
            save_file = f'{av_code}-fanart-{counter}.{suffix}'
            save_path = organized_dir / 'extrafanart' / save_file
            asyncio.create_task(downloader.download_async(fanart_img, save_path))
            counter += 1
            new_fanart.append(save_path.stem)

        imgs_meta.fanart = new_fanart




    def _save_to_nfo(self):
        """保存为nfo文件
        """
        organized_dir = self.organized_file.parent
        self.moive_info.save_to_nfo(organized_dir / 'test.nfo')

    def organize(self):
        """整理文件并保存nfo文件
        """
        shutil.move(self.orgin_file, self.organized_file)
        logger.debug(f'移动文件 {self.orgin_file} 到 {self.organized_file}')
        self._download_imgs()
        self._save_to_nfo()