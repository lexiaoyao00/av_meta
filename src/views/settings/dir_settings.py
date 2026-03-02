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
