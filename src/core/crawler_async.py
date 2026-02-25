import asyncio
from loguru import logger
from typing import Any, Dict, Optional, Union
from curl_cffi import AsyncSession, Response,exceptions
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def return_none_on_failure(retry_state):
    print(f"爬虫重试已耗尽，最后一次异常是: {retry_state.outcome.exception()}")
    return None

class AsyncBaseCrawler:
    def __init__(
        self,
        impersonate: str = "chrome110",
        proxy: Optional[str] = None,
        timeout: int = 30,
        verify: bool = True,
        max_concurrency: int = 10
    ):
        self.impersonate = impersonate
        self.proxy = proxy
        self.timeout = timeout
        self.verify = verify
        self.session: Optional[AsyncSession] = None
        self.max_concurrency = max_concurrency
        self._semaphore = None  # 懒加载信号量

    async def search(self, num_code : str):
        """钩子函数，子类需要实现，搜索番号"""
        pass

    @property
    def semaphore(self):
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrency)
        return self._semaphore

    async def __aenter__(self):
        await self.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def init_session(self):
        """初始化异步 Session"""
        if self.session is None:
            self.session = AsyncSession(
                impersonate=self.impersonate,
                proxies={"http": self.proxy, "https": self.proxy} if self.proxy else None,
                timeout=self.timeout,
                verify=self.verify
            )
        return self.session

    async def close(self):
        """关闭 Session"""
        if self.session:
            await self.session.close()
            self.session = None

    # 使用 tenacity 进行自动重试
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        retry_error_callback=return_none_on_failure,
        reraise=True
    )
    async def request(
        self,
        method: str,
        url: str,
        allow_redirects: bool = True,
        **kwargs
    ) -> Response:
        """底层统一请求方法"""
        async with self.semaphore:
            session = await self.init_session()
            try:
                logger.info(f"[{method.upper()}] -> {url}")
                response : Response = await session.request(method, url,allow_redirects=allow_redirects, **kwargs)
                # 可以在这里统一处理状态码逻辑
                if response.status_code == 404:  # 404 代表不存在，直接返回，不用重试
                    return None
                response.raise_for_status()
                return response
            except Exception as e:
                logger.error(f"请求失败: {url} | 错误: {e}")
                raise e
                # return None

    async def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> Response:
        return await self.request("GET", url, params=params, **kwargs)

    async def post(self, url: str, data: Any = None, json: Any = None, **kwargs) -> Response:
        return await self.request("POST", url, data=data, json=json, **kwargs)

    async def get_json(self, url: str, **kwargs) -> Dict:
        """快捷获取 JSON 结果"""
        resp = await self.get(url, **kwargs)
        return resp.json()
