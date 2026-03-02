import flet as ft

@ft.control
class AppBar(ft.AppBar):
    title : str = "AppBar"
    center_title : bool = False
    bgcolor : ft.Colors = ft.Colors.BLUE

    def init(self):
        self.ref_ibtn_theme_mode = ft.Ref[ft.IconButton]()

        self.actions = [
            ft.IconButton(ft.Icons.NIGHTS_STAY, on_click=self.swith_theme,ref=self.ref_ibtn_theme_mode),
            ft.IconButton(ft.Icons.FILTER_3),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(content="Item 1"),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(
                        content="Checked item",
                        checked=False,
                    ),
                ]
            ),
        ]

    def swith_theme(self, e: ft.Event[ft.IconButton]):
        self.ref_ibtn_theme_mode.current.icon = ft.Icons.WB_SUNNY_OUTLINED if self.ref_ibtn_theme_mode.current.icon == ft.Icons.NIGHTS_STAY else ft.Icons.NIGHTS_STAY
        self.page.theme_mode = ft.ThemeMode.LIGHT if self.page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        self.update()
