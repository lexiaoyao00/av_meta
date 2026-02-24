from spiders.javbus import JavBusSpider
from modules.analysis_file import AnalysisFile
import asyncio
from typing import List,Dict
from schemas.movie import  NfoMovieModel


async def main():
    spider = JavBusSpider()
    # asyncio.run(spider.search('mide-565'))
    # asyncio.run(spider.search('052512-031'))

    file_dir = 'F:/pikpakDownload'
    analysis_file = AnalysisFile(file_dir)
    file_list = analysis_file.get_video_path_list()
    success = analysis_file.extract_av_code(files=file_list)
    tasks:Dict[str,asyncio.Task] = {}
    for file,code in success.items():
        print(file,code)
        task = asyncio.create_task(spider.search(code))
        file_stem = file.split('.')[0]
        tasks[file_stem] = task

    results : List[NfoMovieModel] = await asyncio.gather(*list(tasks.values()))
    for i,result in enumerate(results):
        if result:
            file_stem = list(tasks.keys())[i].split('.')[0]
            save_path = f'output/{file_stem}.nfo'
            result.save_to_nfo(save_path)

if __name__ == '__main__':


    asyncio.run(main())