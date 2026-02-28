import flet as ft
from widgets import DirBrowser
from config import settings
from utils.signals import update_settings_sig,dir_settings_submit_sig

@ft.control
class DirContainer(ft.Container):

    def init(self):
        self._dir_name_map = {
            '输出目录' : 'output_dir',
        }

    def build(self):
        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                DirBrowser(val=settings.output_dir, label="输出目录"),
            ]
        )
        dir_settings_submit_sig.connect(self.oe_dir_settings_changed)

    def oe_dir_settings_changed(self, sender, **kw):
        value = kw.get('value')
        if not value:
            return

        field_str = self._dir_name_map.get(sender)
        if not field_str:
            return

        update_settings_sig.send('settings_dir_container', field=field_str, value=value)

@ft.control
class RuleContainer(ft.Container):
    def init(self):
        self._rule_name_map = {
            '下载图像' : 'download_imgs',
            '移动源文件到输出目录' : 'move_src_file',
        }
        self.ref_download_imgs = ft.Ref[ft.Checkbox]()
        self.ref_move_src_file = ft.Ref[ft.Checkbox]()

    def build(self):
        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Checkbox(label="下载图像", value=settings.download_imgs,ref=self.ref_download_imgs,on_change=self._on_change),
                ft.Checkbox(label="移动源文件到输出目录", value=settings.move_src_file,ref=self.ref_move_src_file,on_change=self._on_change),
            ]
        )

    def _on_change(self, e:ft.Event[ft.Checkbox]):
        # print(e.control.label, e.control.value)
        field_str = self._rule_name_map.get(e.control.label)
        if not field_str:
            return
        update_settings_sig.send('settings_rule_container', field=field_str, value=e.control.value)

@ft.control
class SettingsTabBar(ft.TabBar):
    def __init__(self):
        super().__init__(tabs=[])

    def init(self):
        self.tabs=[
                ft.Tab(label="目录"),
                ft.Tab(label="规则"),
            ]

@ft.control
class SettingsTabBarView(ft.TabBarView):
    def __init__(self):
        super().__init__(controls=[])

    def init(self):
        self.expand = True
        self.controls=[
                DirContainer(),
                RuleContainer()
            ]

@ft.control
class SettingsTabs(ft.Column):
    expand : bool = True

    def init(self):
        self._tab_bar = SettingsTabBar()
        self._tab_bar_view = SettingsTabBarView()
        self.tab_length = len(self._tab_bar.tabs)

    def build(self):
        self.controls = [
            self._tab_bar,
            self._tab_bar_view
        ]


@ft.control
class SettingsView(ft.Container):
    expand : bool = True

    def build(self):
        self.page.appbar.title = 'Settings'
        settings_tabs = SettingsTabs()
        self.content = ft.Tabs(
            length= settings_tabs.tab_length,
            content= settings_tabs
        )
