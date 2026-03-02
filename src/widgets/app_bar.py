import flet as ft

@ft.control
class AppBar(ft.AppBar):
    title : str = "AppBar"
    center_title : bool = False
    bgcolor : ft.Colors = ft.Colors.BLUE

    def init(self):
        self.actions = [
            ft.IconButton(ft.Icons.WB_SUNNY_OUTLINED, on_click=self.swith_theme),
            ft.IconButton(ft.Icons.FILTER_3),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(content="Item 1"),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(
                        content="Checked item",
                        checked=False,
                        on_click=self.handle_checked_item_click,
                    ),
                ]
            ),
        ]


    def handle_checked_item_click(self,e: ft.Event[ft.PopupMenuItem]):
        e.control.checked = not e.control.checked
        self.page.update()

    def swith_theme(self, e: ft.Event[ft.IconButton]):
        self.page.theme_mode = ft.ThemeMode.LIGHT if self.page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        self.page.update()
