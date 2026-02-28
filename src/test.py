from spiders import JavDBSpider
import asyncio
from pprint import pprint

async def test():
    spider = JavDBSpider()
    info = await spider.search('mide-565')
    if info:
        pprint(info.model_dump(exclude_none=True))


if __name__ == '__main__':
    asyncio.run(test())