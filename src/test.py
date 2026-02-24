from spiders.javbus import JavBusSpider
import asyncio


if __name__ == '__main__':
    spider = JavBusSpider()
    asyncio.run(spider.search('mide-565'))
    # asyncio.run(spider.search('052512-031'))