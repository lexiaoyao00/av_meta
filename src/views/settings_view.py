import flet as ft
from widgets import DirBrowser
from config import settings


@ft.control
class DirContainer(ft.Container):

    def build(self):
        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Button(content="保存"),
                DirBrowser(val=settings.output_dir, label="输出目录")
            ]
        )

    def _save_config(self):
        ...

@ft.control
class RuleContainer(ft.Container):

    def build(self):
        self.content = ft.Text("规则组件")

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
