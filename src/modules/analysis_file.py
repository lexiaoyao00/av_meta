from pathlib import Path
import re
from utils.files import judge_file_type,FileType
from typing import Dict,List,Tuple

class AnalysisFile:
    """解析文件, 提取番号"""
    def __init__(self, select_dir : str|Path):
        self.current_dir = Path(select_dir)
        self.pattern = re.compile(r'\b[0-9A-Za-z]+(?:-[0-9A-Za-z]+)*\d\b')


    # 1. 先替换所有下划线为短横
    def normalize(self,text:str) -> str:
        return text.replace("_", "-")


    def get_video_path_list(self) -> list[Path]:
        """获取当前目录下所有视频文件路径"""
        file_list = []
        for file in self.current_dir.iterdir():
            if file.is_file() and judge_file_type(file) == FileType.VIDEO:
                file_list.append(file)

        return file_list

    def _extract_av_code(self, name : str) -> str:
        """从文件名字符串中提取番号"""
        norm_t = self.normalize(name)
        matches = self.pattern.findall(norm_t)
        return matches

    def extract_av_code(self,files:list[Path]):
        """从文件列表中提取番号,
        返回:
            成功:文件和对应的番号字符串
            失败:文件
            不确定:文件及提取到的番号列表
        """
        success : Dict[str,str]  = {}  # 提取成功的文件和番号
        failed : List[str] = []  # 提取失败的文件
        uncertain : Dict[str,List[str]]= {}  # 不确定的文件和番号
        for file in files:
            name = file.name
            stem = file.stem
            matches = self._extract_av_code(stem)
            if not matches:
                failed.append(name)
            elif len(matches) == 1:
                success[name] = matches[0]
            else:
                uncertain[name] = matches

        return (success,failed,uncertain)
