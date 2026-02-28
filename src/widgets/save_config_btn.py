import flet as ft
from config import save_current_settings

@ft.control
class SaveConfigBtn(ft.FloatingActionButton):

    def init(self):
        self.visible = False

    def build(self):
        self.content = "保存"


    def save_config(self):
        save_current_settings()
