import flet as ft
from config import settings
from utils.signals import update_settings_sig


@ft.control
class SpiderOrder(ft.ReorderableListView):

    def init(self):
        self.show_default_drag_handles = False
        self.header = ft.Text("爬虫顺序")
        self.on_reorder = self.handle_reorder
        self.controls=[
            ft.ListTile(
                title=ft.Text(spider_name, color=ft.Colors.BLACK),
                leading=ft.ReorderableDragHandle(
                        content=ft.Icon(ft.Icons.DRAG_INDICATOR),
                        mouse_cursor=ft.MouseCursor.GRAB,
                    )
            )
            for spider_name in settings.spider_order
        ]


    def handle_reorder(self, e: ft.OnReorderEvent):
        e.control.controls.insert(e.new_index, e.control.controls.pop(e.old_index))
        new_order = [c.title.value for c in e.control.controls]
        update_settings_sig.send('settings_rule_container', field='spider_order', value=new_order)

@ft.control
class RuleContainer(ft.Container):
    def init(self):
        self._rule_name_map = {
            '下载图像' : 'download_imgs',
            '移动源文件到输出目录' : 'move_src_file',
        }
        self.ref_download_imgs = ft.Ref[ft.Checkbox]()
        self.ref_move_src_file = ft.Ref[ft.Checkbox]()

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    controls=[
                        ft.Checkbox(label="下载图像", value=settings.download_imgs,ref=self.ref_download_imgs,on_change=self._on_change),
                        ft.Checkbox(label="移动源文件到输出目录", value=settings.move_src_file,ref=self.ref_move_src_file,on_change=self._on_change),
                    ]
                ),
                SpiderOrder(),
            ]
        )

    def _on_change(self, e:ft.Event[ft.Checkbox]):
        # print(e.control.label, e.control.value)
        field_str = self._rule_name_map.get(e.control.label)
        if not field_str:
            return
        update_settings_sig.send('settings_rule_container', field=field_str, value=e.control.value)
