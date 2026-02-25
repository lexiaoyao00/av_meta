from utils.signals import (
    start_scan_sig,
    scan_failed_sig,
    update_metadata_sig,
    show_matadata_sig,
    start_scan_sig,
    scrape_finished_sig,
    )
from modules.analysis_file import AnalysisFile
from loguru import logger
from typing import List
import asyncio
from schemas.movie import  NfoMovieModel
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
        start_scan_sig.connect(self.oe_start_scan)
        scrape_finished_sig.connect(self.oe_scrape_finished)


    async def scrape(self, spider : AsyncBaseCrawler, pending_files : Dict[str,str]):
        file_names = list(pending_files.keys())
        tasks = []
        for file,code in pending_files.items():
            task = asyncio.create_task(spider.search(code))
            tasks.append(task)

        results : List[NfoMovieModel]= await asyncio.gather(*tasks)
        for file,result in zip(file_names,results):
            if result:
                pending_files.pop(file,None)
                logger.debug(f'文件 {file} 爬取成功')
                asyncio.create_task(update_metadata_sig.send_async('controller', file_name=file, metadata=result))
                # file_stem = file.split('.')[0]
                # save_path = f'output/{file_stem}.nfo'
                # result.save_to_nfo(save_path)
                # logger.debug(f'文件 {file} 的番号信息已保存到 {save_path}')
            else:
                logger.debug(f'文件 {file} 爬取暂时失败')
                asyncio.create_task(scan_failed_sig.send_async('controller', failed_file=file, msg="爬取失败"))

    async def oe_start_scan(self, sender, **kw):
        path : str = kw.get('path')
        logger.debug(f'从路径 {path} 开始扫描')
        analysis_file = AnalysisFile(path)
        file_list = analysis_file.get_video_path_list()
        pending_files = await analysis_file.extract_av_code(files=file_list)

        for name,spider_cls in spider_type_dict.items():
            logger.info(f'当前爬虫是 {name}')
            spider = spider_cls()
            await self.scrape(spider, pending_files)
            await asyncio.sleep(1)      # 等待一秒更新数据
            if not self.app_state_manager.app_state.failed_file:    # 如果所有文件都成功，则退出循环
                logger.debug(f'所有文件都成功，退出爬虫循环')
                break

        # show_matadata_sig.send('scaner', metadata=results[0])
        asyncio.create_task(scrape_finished_sig.send_async('controller'))

    async def oe_scrape_finished(self, sender, **kw):
        app_state = self.app_state_manager.app_state
        if not app_state.success_file_metadata:
            return
        failed_files = list(app_state.failed_file.keys())
        logger.info(f'失败的文件有：{failed_files}')
        success_file_metadata = app_state.success_file_metadata
        first_item = next(iter(app_state.success_file_metadata.items()))
        if not first_item:
            return

        for item in success_file_metadata.items():
            organizer = Organizer(item[1], item[0])
            organizer.organize()

        asyncio.create_task(show_matadata_sig.send_async('controller',metadata=first_item[1]))