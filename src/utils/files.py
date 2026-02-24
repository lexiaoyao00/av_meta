from enum import Enum,auto
from pathlib import Path

class FileType(Enum):
    VIDEO = auto()
    TVSHOW = auto()
    SEASON = auto()
    EPISODE = auto()

    UNKNOWN = auto()

class MovieType(Enum):
    MP4 = '.mp4'
    AVI = '.avi'
    RMVB = '.rmvb'
    WMV = '.wmv'
    MOV = '.mov'
    MKV = '.mkv'
    FLV = '.flv'
    TS = '.ts'
    WEBM = '.webm'
    ISO = '.iso'
    MPG = '.mpg'

def judge_file_type(file_name:str|Path):
    file_path = Path(file_name)
    movie_suffix = [suffix.value for suffix in MovieType]
    if file_path.suffix in movie_suffix:
        return FileType.VIDEO
    else:
        return FileType.UNKNOWN