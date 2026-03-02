import flet as ft
from config import settings
from schemas import AvDir

@ft.control
class FormatContainer(ft.Container):
    def init(self):
        av_dir_fields = list(AvDir.model_fields.keys())
        # print(av_dir_fields)
        av_dir_fields_str = ', '.join(av_dir_fields)
        self.content = ft.Column(
            controls=[
                ft.TextField(
                    value=settings.output_dir_name,
                    label='输出目录格式',
                    tooltip="保存nfo时的目录格式",
                    expand=True,
                    ),
                ft.Text(value="当前支持的格式有: {}".format(av_dir_fields_str)),
            ]
        )