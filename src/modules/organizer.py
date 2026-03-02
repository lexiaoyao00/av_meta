from schemas import (
    NfoMovieImageModel,
    AvDir)
from core.downloader import Downloader
from core.app_state import AppStateManager
from pathlib import Path
from config import settings
import shutil
from loguru import logger
from typing import List
import asyncio
from utils.signals import organize_finished_asig



class Organizer:
    """整理文件并保存nfo文件"""
    def __init__(self, file_name : str):
        """根据文件名从app_state中获取信息"""
        self.orgin_file = file_name

        self.moive_info = AppStateManager().app_state.success_file_metadata.get(self.orgin_file).model_copy(deep=True)
        if self.moive_info is None:
            logger.error(f'文件: {self.orgin_file} 没有元数据')
            return

        self.init_dir()

    def init_dir(self):
        """初始化目录"""
        # TODO:整理后的文件路径根据配置来
        str_tmp = settings.output_dir_name

        actor_str = 'Unknown'
        if self.moive_info.actors :
            actor_str = ' '.join([actor.name for actor in self.moive_info.actors])

        actor_str.strip()
        av_dir = AvDir(
            title=self.moive_info.title,
            num_code=self.moive_info.num_code,
            actor= actor_str,
            releasedate = self.moive_info.releasedate or ''
        )
        av_dir_str = str_tmp.format(**av_dir.model_dump())
        if (out_dir := Path(settings.output_dir)).is_absolute():
            self.organized_file = out_dir / av_dir_str / self.orgin_file
        else:
            self.organized_file = Path(settings.select_dir) / settings.output_dir / av_dir_str / self.orgin_file

        self.organized_file.parent.mkdir(parents=True, exist_ok=True)


    def download_imgs(self):
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

        if imgs_meta.extrafanart is not None:
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
        new_poster = save_path.name
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
        new_thumb = save_path.name
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
        for fanart_img in imgs_meta.extrafanart:
            suffix = fanart_img.split('.')[-1]
            save_file = f'{av_code}-fanart-{counter}.{suffix}'
            save_path = organized_dir / 'extrafanart' / save_file
            asyncio.create_task(downloader.download_async(fanart_img, save_path))
            counter += 1
            new_fanart.append(save_path.name)

        imgs_meta.extrafanart = new_fanart


    def _save_to_nfo(self):
        """保存为nfo文件
        """
        output_dir = self.organized_file.parent
        file_stem = self.organized_file.stem
        nfo_path = output_dir / f'{file_stem}.nfo'
        self.moive_info.save_to_nfo(nfo_path)
        logger.debug(f'文件 {self.orgin_file} 的番号信息已保存')

    def organize(self):
        """整理文件并保存nfo文件
        """
        if settings.move_src_file:
            print('整理时的文件路径状态:', AppStateManager().app_state.files_path)
            file_path = AppStateManager().app_state.files_path.get(self.orgin_file)
            if file_path is None:
                logger.error(f'文件: {self.orgin_file} 没有获取到实际路径')
                return
            logger.info(f'移动文件 {str(file_path)} 到 {self.organized_file}')
            self.organized_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(file_path, self.organized_file)

        if settings.download_imgs:
            logger.info(f'开始下载 {self.orgin_file} 的图片')
            self.download_imgs()

        self._save_to_nfo()

        file_name = self.organized_file.name
        asyncio.create_task(organize_finished_asig.send_async('organizer', file_name = file_name))