from pydantic import BaseModel,model_validator,model_serializer
from typing import List,Literal, Optional,Any
from pathlib import Path
import xmltodict

NFO_TYPE = Literal['movie','episodedetails','tvshow']


# 格式参照 https://kodi.wiki/view/NFO_files/Templates#Movie_Template

class NfoActorModel(BaseModel):
    """emby 的角色元数据模型"""
    name : str             # 名称
    role : str = '女优'             # 角色
    order : Optional[int] = None  # 排序
    thumb : Optional[str] = None  # 缩略图


class NfoMovieImageModel(BaseModel):
    """emby 的图片元数据模型"""
    poster : Optional[str] = None  # 海报(实际显示的封面)
    extrafanart : Optional[List[str]] = None  # 剧照
    thumb : Optional[str] = None  # 缩略图

class NfoMovieTagModel(BaseModel):
    """emby 的类标签元数据模型"""
    tag: Optional[List[str]] = None  # 标签
    genre : Optional[List[str]] = None    # 类型

class NfoMovieProductionModel(BaseModel):
    """emby 的制作团队元数据模型"""
    director : Optional[str] = None  # 导演
    writer : Optional[str] = None  # 编剧
    studio : Optional[str] = None  # 工作室/制作商
    publisher : Optional[str] = None  # 发行商


class NfoMovieIntroductionModel(BaseModel):
    """emby 的简介元数据模型"""
    plot : Optional[str] = None  # 简介（概要）
    outline : Optional[str] = None  # 概要
    tagline : Optional[str] = None  # 宣传语

class NfoMovieSetModel(BaseModel):
    """emby 的合集元数据模型"""
    name : str

class NfoMovieModel(BaseModel):
    """emby 的元数据模型"""
    num_code : str          # 番号
    website : str           # 爬取元数据的链接

    title : Optional[str] = None           # 标题
    sorttitle: Optional[str] = None    # 排序标题
    originaltitle:Optional[str] = None  # 原始标题

    premiered : Optional[str] = None  # 首映日期
    releasedate : Optional[str] = None  # 上映日期
    # runtime : int = None  # 时长（分钟） 由emby自己解析即可
    set : Optional[NfoMovieSetModel] = None  # 合集(系列)

    rating : Optional[float] = None   # 社区评分
    criticrating : Optional[float] = None  # 影评人评分

    actors : Optional[List[NfoActorModel]] = None  # 演员

    introduction_meta : Optional[NfoMovieIntroductionModel] = None  # 简介元数据

    production_meta : Optional[NfoMovieProductionModel] = None  # 制作团队元数据

    tag_meta : Optional[NfoMovieTagModel] = None  # 标签元数据

    imgs_meta : Optional[NfoMovieImageModel] = None  # 图片元数据


    def save_to_nfo(self, save_path: Path|str, nfo_type:NFO_TYPE = 'movie'):
        data = {nfo_type:self.model_dump(exclude_none=True)}
        xml_str = xmltodict.unparse(data, pretty=True)

        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(xml_str)

    # 自动打平：将所有子模型的字段提取到顶层
    @model_serializer(mode='wrap')
    def serialize_model(self, handler) -> dict[str, Any]:
        # 1. 获取当前模型原始的序列化结果
        result = handler(self)
        flattened = {}

        # 2. 遍历所有字段
        for field_name, value in result.items():
            # 获取该字段在实例中的原始对象
            original_value = getattr(self, field_name)

            # 3. 如果该字段是一个 Pydantic 模型，则打平它
            if isinstance(original_value, BaseModel):
                # 递归调用该模型的 dump，确保深层嵌套也能处理
                nested_dict = original_value.model_dump(exclude_none=True)
                flattened.update(nested_dict)
            else:
                # 否则保持原样
                flattened[field_name] = value

        return flattened

    # 自动组装：将顶层字段重新分配给对应的子模型
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, data: Any) -> Any:
        # 如果输入是字典，并且没有 子元素 键（说明是打平的格式）
        if not isinstance(data, dict):
            return data

        # 遍历父模型定义的字段，寻找嵌套模型
        for field_name, field_info in cls.model_fields.items():
            # 获取字段的类型类
            target_model = field_info.annotation

            # 判断该字段是否是一个 Pydantic 模型类
            if isinstance(target_model, type) and issubclass(target_model, BaseModel):
                # 如果输入数据中没有这个子模型的键，说明它是打平的
                if field_name not in data:
                    # 获取子模型定义的所有字段名
                    sub_model_fields = target_model.model_fields.keys()
                    # 提取属于该子模型的数据
                    sub_data = {
                        f: data.pop(f) for f in list(data.keys())
                        if f in sub_model_fields
                    }
                    # 重新包装回子模型键下
                    data[field_name] = sub_data

        return data