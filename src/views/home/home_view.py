import flet as ft
from .main_body import MainBody
from .side_info_area import SideInfoArea

@ft.control
class HomeView(ft.Container):
    expand : bool = True

    def init(self):
        self.content = ft.Row(
            expand=True,
            vertical_alignment  = ft.CrossAxisAlignment.START,
            controls=[
                MainBody(),
                SideInfoArea()
            ]
        )

    def build(self):
        self.page.appbar.title = "Home"





