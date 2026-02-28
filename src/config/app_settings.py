from pydantic import BaseModel, Field, model_validator,ConfigDict
from pathlib import Path
import json
from typing import Any

PRO_PATH = Path(__file__).parent.parent.parent


class BaseSettings(BaseModel):

    # 目录管理
    select_dir : str = None # 选择目录, 待搜刮文件资源的存放目录
    output_dir : str = None # 输出目录, 默认None为资源目录下的 output 文件夹
    log_dir : str = None # 日志目录, 默认None为资源目录下的 log 文件夹


    # 选项管理
    download_imgs : bool = True # 是否下载图片
    move_src_file : bool = False # 是否移动源文件到输出目录

    # 格式管理
    output_dir_name : str = '{actor}/{num_code}-{title}-{releasedate}' # 输出文件目录格式

    # ========== 数据验证 ==========
    @model_validator(mode="after")
    def _model_validate(self):
        if self.output_dir is None:
            self.output_dir = "output"
        if self.log_dir is None:
            self.log_dir = str(PRO_PATH / "log")
        return self

class Settings(BaseSettings):

    model_config = ConfigDict(validate_assignment=True)

    def update_field(self, field: str, value):
        """提供一个方法用来更新模型的某个属性"""
        if not hasattr(self, field):
            raise AttributeError(f"'{field}' 不是有效字段")
        setattr(self, field, value)

CONFIG_PATH = PRO_PATH / 'config.json'

def load_config() -> Settings:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Settings(**data)
    else:
        config = Settings()
        save_settings(config)
        return config


def save_settings(settings: Settings):
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        json.dump(settings.model_dump(exclude_none=True), f, ensure_ascii=False, indent=4)