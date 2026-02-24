import asyncio
from curl_cffi import Session,AsyncSession,Response
from utils.decorator import singleton
from utils.signals import download_progress_sig
import time
from loguru import logger

@singleton
class Downloader:
    def __init__(
            self,
            impersonate: str = "chrome110",
            timeout: int = 30,
            max_concurrency: int = 5):
        """
        :param impersonate: 指定模拟的浏览器指纹
        :param timeout: 超时时间
        """
        self.impersonate = impersonate
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        self.cookies = None
        self.max_concurrency = max_concurrency
        self._semaphore = None

    @property
    def semaphore(self):
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrency)
        return self._semaphore

    def _get_file_size(self, response:Response) -> int:
        return int(response.headers.get("Content-Length", 0))

    def _emit_progress(self, file_path: str, current: int, total: int, last_emit_time: float, interval: float = 0.1):
        """
        内部方法：处理进度信号的触发逻辑（含节流）
        :return: 返回本次触发的时间，供下次对比
        """
        now = time.time()
        # 只有满足以下条件才触发信号：
        # 1. 距离上次触发超过了 interval (默认0.1秒)
        # 2. 或者文件下载完成了 (current == total)
        if now - last_emit_time >= interval or current == total:
            # 发送信号
            download_progress_sig.send(
                'downloader',
                file_path=file_path,
                current=current,
                total=total,
                percentage=round(current / total * 100, 2) if total > 0 else 0
            )
            return now
        return last_emit_time

    def download_sync(self, url: str, save_path: str, chunk_size: int = 1024 * 64):
        """
        同步下载方法
        """
        last_emit_time = 0
        logger.debug(f"[Sync] 开始下载: {url}")
        with Session(impersonate=self.impersonate) as s:
            # stream=True 是大文件下载的关键
            r = s.get(url, stream=True, timeout=self.timeout, headers=self.headers,cookies=self.cookies)
            r.raise_for_status()
            total_size = self._get_file_size(r)
            downloaded = 0

            with open(save_path, "wb") as f:
                for chunk in r.aiter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        last_emit_time = self._emit_progress(
                            file_path=save_path,
                            current=downloaded,
                            total=total_size,
                            last_emit_time=last_emit_time
                        )

        logger.info(f"\n[Sync] 下载完成: {save_path}")

    async def download_async(self, url: str, save_path: str, chunk_size: int = 1024 * 64):
        """
        异步下载方法
        """
        logger.debug(f"[Async] 开始下载: {url}")
        async with self.semaphore:
            last_emit_time = 0
            async with AsyncSession(impersonate=self.impersonate) as s:
                # 异步模式同样需要 stream=True
                r = await s.get(url, stream=True, timeout=self.timeout, headers=self.headers,cookies=self.cookies)
                r.raise_for_status()
                total_size = self._get_file_size(r)
                downloaded = 0

                with open(save_path, "wb") as f:
                    # 异步迭代器读取 chunk aiter_content
                    async for chunk in r.aiter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)

                        last_emit_time = self._emit_progress(
                            file_path=save_path,
                            current=downloaded,
                            total=total_size,
                            last_emit_time=last_emit_time
                        )
        logger.info(f"\n[Async] 下载完成: {save_path}")