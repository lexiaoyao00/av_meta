import flet as ft
import asyncio
from utils.signals import (
    show_matadata_asig,
    organize_finished_asig,
    clean_metainfo_sig,
    scrape_finished_asig,
    )
from core import state_manager
from widgets import Prompt


@ft.control
class FileTile(ft.ListTile):
    def __init__(self, file_name : str, success : bool = True):
        self.file_name = file_name
        self.success = success
        super().__init__(title=self.file_name)

    def init(self):
        if self.success:
            self.on_click = self.show_meta
        else:
            self.on_click = self.show_msg


    def show_meta(self, e : ft.Event[ft.ListTile]):
        # print(e)
        # print(e.control.title)
        # file_name : str = e.control.title
        meta_info = state_manager.app_state.success_file_metadata.get(self.file_name)
        if meta_info:
            asyncio.create_task(show_matadata_asig.send_async('file_tile',metadata=meta_info))


    def show_msg(self, e : ft.Event[ft.ListTile]):
        # print(e)
        # file_name : str = e.control.title
        msg = state_manager.app_state.failed_file.get(self.file_name)
        if msg:
            self.page.show_dialog(Prompt(msg))

@ft.control
class SideInfoArea(ft.Container):
    width : int = 300
    vertical_alignment : ft.CrossAxisAlignment = ft.CrossAxisAlignment.START

    def init(self):
        self.ref_success_et = ft.Ref[ft.ExpansionTile]()
        self.ref_fail_et = ft.Ref[ft.ExpansionTile]()

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Text("侧边栏"),
                ft.ExpansionTile(
                    title='成功',
                    expand=True,
                    ref=self.ref_success_et,
                    controls=[],
                    expanded=True
                ),
                ft.ExpansionTile(
                    title='失败',
                    expand=True,
                    ref=self.ref_fail_et,
                    controls=[]
                )
            ]
        )

        organize_finished_asig.connect(self.oe_organize_finished)
        scrape_finished_asig.connect(self.oe_scan_failed)
        clean_metainfo_sig.connect(self.oe_clean_metainfo)

    def append_success(self, file_name : str):
        self.ref_success_et.current.controls.append(FileTile(file_name=file_name))
        self.ref_success_et.current.update()

    def append_fail(self, file_name : str):
        self.ref_fail_et.current.controls.append(FileTile(file_name=file_name,success=False))
        self.ref_fail_et.current.update()


    def clean_value(self):
        self.ref_success_et.current.controls.clear()
        self.ref_fail_et.current.controls.clear()

        self.update()

    async def oe_scan_failed(self, sender, **kw):
        failed_files = list(state_manager.app_state.failed_file.keys())
        self.ref_fail_et.current.controls = [FileTile(file_name=file_name,success=False) for file_name in failed_files]
        self.ref_fail_et.current.update()

    async def oe_organize_finished(self, sender, **kw):
        file_name : str = kw.get('file_name')
        if file_name:
            self.append_success(file_name)

    def oe_clean_metainfo(self, sender, **kw):
        self.clean_value()
