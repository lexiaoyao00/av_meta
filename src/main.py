import flet as ft
from widgets import NavDrawer,AppBar
from utils.signals import nav_sig,start_scan_sig,scan_failed_sig,update_metadata_sig,show_matadata_sig
from views import HomeView, SettingsView
from config import save_current_settings
import sys
from modules.analysis_file import AnalysisFile
from loguru import logger
from typing import Dict,List
import asyncio
from schemas.movie import  NfoMovieModel
from spiders.javbus import JavBusSpider


NAV_ROUTES = {
    0: HomeView(),
    1: SettingsView(),
}


async def oe_start_test(sender, **kw):
    path : str = kw.get('path')
    # print(f"test_start called, path: {path}")
    logger.debug(f'从路径 {path} 开始扫描')
    analysis_file = AnalysisFile(path)
    file_list = analysis_file.get_video_path_list()
    success = analysis_file.extract_av_code(files=file_list)

    file_names = list(success.keys())

    tasks = []
    spider = JavBusSpider()
    for file,code in success.items():
        task = asyncio.create_task(spider.search(code))
        tasks.append(task)

    results : List[NfoMovieModel]= await asyncio.gather(*tasks)
    failed_files = []
    for file,result in zip(file_names,results):
        if result:
            logger.debug(f'文件 {file} 的番号是 {result.num_code}')
            update_metadata_sig.send('scaner', file_name=file, metadata=result)
            file_stem = file.split('.')[0]
            save_path = f'output/{file_stem}.nfo'
            result.save_to_nfo(save_path)
            logger.debug(f'文件 {file} 的番号信息已保存到 {save_path}')
        else:
            logger.debug(f'文件 {file} 的番号未找到')
            failed_files.append(file)

    if failed_files:
        scan_failed_sig.send('scaner', failed_files=failed_files, msg="爬取失败")

    show_matadata_sig.send('scaner', metadata=results[0])



def main(page: ft.Page):
    page.scroll = ft.ScrollMode.AUTO

    body_content = HomeView()

    def oe_nav_by_index(sender,**kw):
        idx = kw.get('index')
        content = NAV_ROUTES.get(idx)
        if not content:
            raise Exception("未知的导航索引")

        body_content.content = content
        body_content.update()

    nav_sig.connect(oe_nav_by_index,'nav_drawer',False)
    start_scan_sig.connect(oe_start_test,'start_scan')

    async def on_close(e):
        save_current_settings()
        await page.window.destroy()
        sys.exit(0)

    page.on_close = on_close

    page.appbar = AppBar()
    page.drawer = NavDrawer()
    page.add(body_content)





if __name__ == "__main__":
    ft.run(main)