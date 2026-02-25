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
from spiders.javbus import JavBusSpider
from utils.decorator import singleton
from core.app_state import AppStateManager
from modules.organizer import Organizer
from utils.tool_func import sync_wrapper

@singleton
class Controller:
    """控制流程,实现一些槽函数"""
    def __init__(self):
        self.app_state_manager = AppStateManager()
        start_scan_sig.connect(self.oe_start_scan)
        scrape_finished_sig.connect(self.oe_scrape_finished)


    async def oe_start_scan(self, sender, **kw):
        path : str = kw.get('path')
        # print(f"test_start called, path: {path}")
        logger.debug(f'从路径 {path} 开始扫描')
        analysis_file = AnalysisFile(path)
        file_list = analysis_file.get_video_path_list()
        success = await analysis_file.extract_av_code(files=file_list)

        file_names = list(success.keys())

        tasks = []
        spider = JavBusSpider()
        for file,code in success.items():
            task = asyncio.create_task(spider.search(code))
            tasks.append(task)

        results : List[NfoMovieModel]= await asyncio.gather(*tasks)
        for file,result in zip(file_names,results):
            if result:
                logger.debug(f'文件 {file} 的番号是 {result.num_code}')
                asyncio.create_task(update_metadata_sig.send_async('controller', file_name=file, metadata=result))
                # file_stem = file.split('.')[0]
                # save_path = f'output/{file_stem}.nfo'
                # result.save_to_nfo(save_path)
                # logger.debug(f'文件 {file} 的番号信息已保存到 {save_path}')
            else:
                logger.debug(f'文件 {file} 的番号未找到')
                asyncio.create_task(scan_failed_sig.send_async('controller', failed_file=file, msg="爬取失败"))


        # show_matadata_sig.send('scaner', metadata=results[0])
        asyncio.create_task(scrape_finished_sig.send_async('controller'))

    async def oe_scrape_finished(self, sender, **kw):
        app_state = self.app_state_manager.app_state
        if not app_state.success_file_metadata:
            return
        first_item = next(iter(app_state.success_file_metadata.items()))
        # print(first_item)
        organizer = Organizer(first_item[1], first_item[0])
        organizer.organize()
        asyncio.create_task(show_matadata_sig.send_async('controller',metadata=first_item[1]))