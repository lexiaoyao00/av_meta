from curl_cffi import Session, Response
from typing import Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class SyncBaseCrawler:
    def __init__(self, impersonate: str = "chrome110", proxy: Optional[str] = None, timeout: int = 30):
        self.session = Session(
            impersonate=impersonate,
            proxies={"http": proxy, "https": proxy} if proxy else None,
            timeout=timeout
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def request(self, method: str, url: str, **kwargs) -> Response:
        logger.info(f"[Sync {method.upper()}] -> {url}")
        resp = self.session.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)
