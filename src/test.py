from core.downloader import Downloader
from utils.signals import download_progress_sig
import asyncio

def oe_progress(sender, **kw):
    print(kw)


async def main():
    download_progress_sig.connect(oe_progress)
    href="https://cdn.donmai.us/original/a4/36/__doro_and_d_goddess_of_victory_nikke_drawn_by_soft_mizu__a436abc5b06c78966db588064ce8b8c7.jpg?download=1"
    d = Downloader()
    await d.download_async(url=href, save_path='test.jpg')

if __name__ == '__main__':
    asyncio.run(main())