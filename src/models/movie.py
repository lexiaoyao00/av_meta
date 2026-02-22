from tortoise import fields, models
from typing import List


class Actor(models.Model):
    """emby 的角色元数据模型"""
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)
    role = fields.CharField(max_length=255)

    movies : fields.ManyToManyRelation['MovieMeta']

    def __str__(self):
        return self.name

class Director(models.Model):
    """emby 的导演元数据模型"""
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)

    movies : fields.ManyToManyRelation['MovieMeta']

    def __str__(self):
        return self.name

class Writer(models.Model):
    """emby 的编剧元数据模型"""
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)

    movies : fields.ManyToManyRelation['MovieMeta']

    def __str__(self):
        return self.name

class Studio(models.Model):
    """emby 的工作室元数据模型"""
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)

    movies : fields.ManyToManyRelation['MovieMeta']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """emby 的标签元数据模型"""
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)

    movies : fields.ManyToManyRelation['MovieMeta']

    def __str__(self):
        return self.name


class MovieMeta(models.Model):
    """
    emby 的元数据模型
    番号(num_code)唯一且必须
    标题(title)必须
    排序标题(sorttitle)必须
    """
    id = fields.IntField(pk=True)

    website = fields.CharField(max_length=255, null=True)  # 链接
    num_code = fields.CharField(max_length=255,unique=True)  # 番号

    title = fields.CharField(max_length=255)        # 标题
    sorttitle = fields.CharField(max_length=255, null=True)  # 排序标题
    original_title = fields.CharField(max_length=255, null=True)    # 原始标题

    rating = fields.FloatField(null=True)   # 社区评分
    criticrating = fields.FloatField(null=True) # 影评人评分

    mpaa = fields.CharField(max_length=255, null=True)           # 家长评级
    customrating = fields.CharField(max_length=255, null=True)  # 自定义评级

    plot = fields.TextField(null=True)  # 简介（概要）
    outline = fields.TextField(null=True)  # 概要
    tagline = fields.CharField(max_length=255, null=True)  # 宣传语

    director : fields.ManyToManyRelation[Director] = fields.ManyToManyField('meta.Director', related_name='movies')    # 导演
    writer : fields.ManyToManyRelation[Writer] = fields.ManyToManyField('meta.Writer', related_name='movies')  # 编剧
    actors : fields.ManyToManyRelation[Actor] = fields.ManyToManyField('meta.Actor', related_name='movies')  # 演员

    studio : fields.ManyToManyRelation[Studio] = fields.ManyToManyField('meta.Studio', related_name='movies')  # 工作室
    tag : fields.ManyToManyRelation[Tag] = fields.ManyToManyField('meta.Tag', related_name='movies')  # 标签
    genre : fields.ManyToManyRelation[Tag] = fields.ManyToManyField('meta.Tag', related_name='movies')    # 类型

    poster = fields.CharField(max_length=255, null=True)  # 封面
    fanart = fields.CharField(max_length=255, null=True)  # 海报背景
    thumb = fields.CharField(max_length=255, null=True)  # 缩略图

    # TODO: 添加更多字段

    def __str__(self):
        return self.num_code