
from pydantic import BaseModel
from typing import List, Dict
from schemas.movie import  NfoMovieModel
from utils.decorator import singleton
from utils.signals import (
    update_metadata_sig,
    scan_failed_sig,
    del_failed_file_sig,
    analysis_file_sig,
    )
from loguru import logger
import asyncio
from pathlib import Path

class AppState(BaseModel):
    """
    用来保存当前搜刮状态，如成功的元数据
    """
    files_path : Dict[str,Path] = {} # 保存文件名 -> 文件路径, 方便移动文件, 在解析文件时可以直接赋值
    success_file_metadata: Dict[str, NfoMovieModel] = {} # 保存成功获取的元数据, 文件名 -> 元数据
    failed_file: Dict[str,str] = {} # 保存获取元数据失败的文件名和失败原因

@singleton
class AppStateManager:
    """
    管理软件状态，定义一些方法
    """

    def __init__(self):
        self.app_state = AppState()
        self._async_lock = asyncio.Lock()

        update_metadata_sig.connect(self.oe_update_metadata)
        scan_failed_sig.connect(self.update_failed_file)
        del_failed_file_sig.connect(self.ov_del_failed_file)
        analysis_file_sig.connect(self.oe_set_files_path)

    def oe_set_files_path(self, sender, **kw):
        """
        设置文件路径
        """
        files_path : Dict[str,str] = kw.get("files_path")
        if files_path is None:
            logger.error("设置文件路径失败,参数错误")
            return
        self.app_state.files_path = files_path

    def clean_previous_scan(self):
        """
        清理前面的扫描结果
        """
        logger.info("开始扫描，清理前面的扫描结果")
        self.app_state.success_file_metadata.clear()
        self.app_state.failed_file.clear()


    async def oe_update_metadata(self, sender, **kw):
        """
        更新元数据
        """
        file_name: str = kw.get("file_name")
        metadata: NfoMovieModel = kw.get("metadata")
        if file_name is None or metadata is None:
            logger.error("更新元数据失败,参数错误")
            return
        async with self._async_lock:
            logger.debug(f"更新成功文件: {file_name}")
            self.app_state.success_file_metadata[file_name] = metadata

    async def update_failed_file(self, sender, **kw):
        """
        更新失败文件
        """
        failed_file:List[str] = kw.get("failed_file")
        msg:str = kw.get("msg","未知原因")
        if not failed_file:
            logger.warning("更新失败文件失败,传入文件为空")
            return
        async with self._async_lock:
            logger.debug(f"更新失败文件: {failed_file}")
            self.app_state.failed_file[failed_file] = msg

    async def ov_del_failed_file(self, sender, **kw):
        """
        删除失败文件, 前面失败的文件在成功后需要删除
        """
        file_name: str = kw.get("file_name")
        if file_name is None:
            logger.warning("删除失败文件失败,文件名为空")
            return
        async with self._async_lock:
            logger.debug(f"从失败文件中删除: {file_name}")
            self.app_state.failed_file.pop(file_name, None)