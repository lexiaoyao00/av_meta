from core.downloader import Downloader
from spiders.javbus import javbus_cookies,javbus_headers

imgs = [
    'https://www.javbus.com/pics/thumb/1qee.jpg',
    'https://www.javbus.com/pics/cover/1qee_b.jpg'
]

downloader = Downloader()
downloader.cookies = javbus_cookies
downloader.headers = javbus_headers

for img in imgs:
    file = img.split('/')[-1]
    downloader.download_sync(img, file)

