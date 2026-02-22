import flet as ft
from config import settings
from widgets import Error
from utils.signals import start_scan_sig,update_settings_sig
@ft.control
class SearchRow(ft.Row):
    expand : bool = True

    def init(self):
        self.ref_dir_tf = ft.Ref[ft.TextField]()
        self.ref_select_btn = ft.Ref[ft.Button]()
        self.ref_start_btn = ft.Ref[ft.Button]()
        self._select_dir = settings.select_dir or ""

    def build(self):
        self.controls = [
            ft.TextField(label='当前目录',
                         value=self._select_dir,
                         ref=self.ref_dir_tf,
                         read_only=True,),
            ft.Button("选择目录", on_click=self.select_dir,ref=self.ref_select_btn),
            ft.Button("开始", on_click=self.start, ref=self.ref_start_btn),
        ]

    async def select_dir(self, e):
        path = await ft.FilePicker().get_directory_path()
        self._select_dir = path or self._select_dir
        self.ref_dir_tf.current.value = self._select_dir
        self.ref_dir_tf.current.update()
        update_settings_sig.send('start_scan', field='select_dir', value=self._select_dir)


    def start(self, e):
        if not self._select_dir:
            self.page.show_dialog(Error("请先选择目录"))
            return

        start_scan_sig.send('start_scan', path = self._select_dir)


@ft.control
class HomeView(ft.Container):
    expand : bool = True

    def build(self):
        self.page.appbar.title = "Home"
        self.content = ft.Column(
            expand=True,
            scroll= ft.ScrollMode.AUTO,
            controls=[
                SearchRow(),
            ]
        )

    def show_meta(self):
        ...