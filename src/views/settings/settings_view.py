import flet as ft

from .dir_settings import DirContainer
from .rule_settings import RuleContainer
from .format_settingss import FormatContainer
@ft.control
class SettingsTabBar(ft.TabBar):
    def __init__(self):
        super().__init__(tabs=[])

    def init(self):
        self.tabs=[
                ft.Tab(label="目录"),
                ft.Tab(label="规则"),
                ft.Tab(label="格式")
            ]

@ft.control
class SettingsTabBarView(ft.TabBarView):
    def __init__(self):
        super().__init__(controls=[])

    def init(self):
        self.expand = True
        self.controls=[
                DirContainer(),
                RuleContainer(),
                FormatContainer()
            ]

@ft.control
class SettingsTabs(ft.Column):
    expand : bool = True

    def init(self):
        self._tab_bar = SettingsTabBar()
        self._tab_bar_view = SettingsTabBarView()
        self.tab_length = len(self._tab_bar.tabs)

        self.controls = [
            self._tab_bar,
            self._tab_bar_view
        ]


@ft.control
class SettingsView(ft.Container):
    expand : bool = True

    def init(self):
        settings_tabs = SettingsTabs()
        self.content = ft.Tabs(
            length= settings_tabs.tab_length,
            content= settings_tabs
        )

    def build(self):
        self.page.appbar.title = 'Settings'

