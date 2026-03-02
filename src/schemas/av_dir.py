from pydantic import BaseModel


class AvDir(BaseModel):
    """视频保存的目录关键字"""
    title : str
    num_code : str
    actor : str = 'Unknown'
    releasedate : str = ''