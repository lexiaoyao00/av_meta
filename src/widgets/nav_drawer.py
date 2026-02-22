import flet as ft
from utils.signals import nav_sig


class NavDrawer(ft.NavigationDrawer):

    def __init__(self, end_drawer:bool = False):
        super().__init__()
        self._end_drawer = end_drawer

    def init(self):
        self._home_nav = ft.Ref[ft.NavigationDrawerDestination]()
        self._settings_nav = ft.Ref[ft.NavigationDrawerDestination]()

        self.on_change = self.handle_change
        # self.on_dismiss = self.handle_dismissal


    def build(self):
        self.controls = [
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="主页",
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.HOME),
                ref=self._home_nav,
            ),
            ft.NavigationDrawerDestination(
                label="设置",
                icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED),
                selected_icon=ft.Icons.SETTINGS,
                ref=self._settings_nav,
            ),
        ]


    # def handle_dismissal(self, e: ft.Event[ft.NavigationDrawer]):
    #     print("Drawer dismissed!")

    async def handle_change(self,e: ft.Event[ft.NavigationDrawer]):
        nav_sig.send('nav_drawer', index=e.control.selected_index)
        if self._end_drawer:
            await self.page.close_end_drawer()
        else:
            await self.page.close_drawer()