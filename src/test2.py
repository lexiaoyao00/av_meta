from spiders.jav123 import Jav123Spider
import asyncio

async def main():
    spider = Jav123Spider()
    await spider.search('mide-565')

if __name__ == '__main__':
    asyncio.run(main())
