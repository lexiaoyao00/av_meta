from utils.signals import (
    start_scan_asig,
    scan_failed_asig,
    update_metadata_asig,
    show_matadata_asig,
    scrape_finished_asig,
    organize_finished_asig,
    )
from modules.analysis_file import AnalysisFile
from loguru import logger
from typing import List
import asyncio
from schemas import  NfoMovieModel
from core.crawler_async import AsyncBaseCrawler
from spiders import spider_type_dict
from utils.decorator import singleton
from core.app_state import AppStateManager
from modules.organizer import Organizer
from typing import Dict

@singleton
class Controller:
    """控制流程,实现一些槽函数"""
    def __init__(self):
        self.app_state_manager = AppStateManager()
        start_scan_asig.connect(self.oe_start_scan)
        scrape_finished_asig.connect(self.oe_scrape_finished)
        organize_finished_asig.connect(self.oe_organize_finished)
        self._is_running = False


    async def scrape(self,spider_name : str, spider : AsyncBaseCrawler, pending_files : Dict[str,str]):
        file_names = list(pending_files.keys())
        tasks = []
        for file,code in pending_files.items():
            task = asyncio.create_task(spider.search(code))
            tasks.append(task)

        results : List[NfoMovieModel]= await asyncio.gather(*tasks)
        for file,result in zip(file_names,results):
            if result:
                pending_files.pop(file,None)
                logger.info(f'文件 {file} 在 {spider_name} 爬虫中爬取成功')
                asyncio.create_task(update_metadata_asig.send_async('controller', file_name=file, metadata=result))
                # file_stem = file.split('.')[0]
                # save_path = f'output/{file_stem}.nfo'
                # result.save_to_nfo(save_path)
                # logger.debug(f'文件 {file} 的番号信息已保存到 {save_path}')
            else:
                logger.info(f'文件 {file} 在 {spider_name} 爬虫中爬取失败')
                asyncio.create_task(scan_failed_asig.send_async('controller', failed_file=file, msg="爬取失败"))

    async def oe_start_scan(self, sender, **kw):
        if self._is_running:
            logger.warning('爬虫已经在运行中, 稍后再试')
            return
        self.app_state_manager.clean_previous_scan()
        self._is_running = True
        path : str = kw.get('path')
        logger.debug(f'从路径 {path} 开始扫描')

        analysis_file = AnalysisFile(path)
        file_list = analysis_file.get_video_path_list()
        pending_files = await analysis_file.extract_av_code(files=file_list)

        for name,spider_cls in spider_type_dict.items():
            logger.info(f'当前爬虫是 {name}')
            spider = spider_cls()
            await self.scrape(name, spider, pending_files)
            await asyncio.sleep(1)      # 等待一秒更新数据
            if not self.app_state_manager.app_state.failed_file:    # 如果所有文件都成功，则退出循环
                logger.debug(f'所有文件都成功，退出爬虫循环')
                break

        asyncio.create_task(scrape_finished_asig.send_async('controller'))

    async def oe_scrape_finished(self, sender, **kw):
        if not self.app_state_manager.app_state.success_file_metadata:
            logger.error('没有成功爬取的文件')
            return
        app_state = self.app_state_manager.app_state
        failed_files = list(app_state.failed_file.keys())
        logger.info(f'失败的文件有：{failed_files}')
        success_file_metadata = app_state.success_file_metadata

        self._is_running = False
        for file_name in list(success_file_metadata.keys()):
            organizer = Organizer(file_name)
            organizer.organize()

    async def oe_organize_finished(self, sender, **kw):
        file_name = kw.get('file_name')
        if not file_name:
            logger.error('oe_organize_finished 没有获取到文件名')
            return

        meta_data = self.app_state_manager.app_state.success_file_metadata.get(file_name)
        if not meta_data:
            logger.error(f'oe_organize_finished 没有获取到文件 {file_name} 的元数据')
            return

        # first_item = next(iter(self.app_state_manager.app_state.success_file_metadata.items()))


        asyncio.create_task(show_matadata_asig.send_async('controller',metadata=meta_data))
