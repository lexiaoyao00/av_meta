
from pydantic import BaseModel
from typing import List, Dict
from schemas.movie import  NfoMovieModel
from utils.decorator import singleton
from utils.signals import update_metadata_sig

class AppState(BaseModel):
    """
    用来保存当前搜刮状态，如成功的元数据
    """
    success_file_metadata: Dict[str, NfoMovieModel] = {} # 保存成功获取的元数据, 文件 -> 元数据
    failed_file: List[str] = [] # 保存获取元数据失败的文件名

@singleton
class AppStateManager:
    """
    管理软件状态，定义一些方法
    """

    def __init__(self):
        self.app_state = AppState()

        update_metadata_sig.connect(self.update_metadata)


    def update_metadata(self, file_name: str, metadata: NfoMovieModel):
        """
        更新元数据
        """
        self.app_state.success_file_metadata[file_name] = metadata

    def update_failed_file(self, failed_files:List[str], msg:str="未知原因"):
        """
        更新失败文件
        """
        self.app_state.failed_file.extend(failed_files)