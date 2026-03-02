import flet as ft
from utils.signals import (
    analysis_file_sig,
    scan_success_asig,
    start_scan_asig
    )

@ft.control
class CrawlerProgress(ft.Row):

    def init(self):
        self._total = 0
        self._current = 0


        self.ref_progress_bar = ft.Ref[ft.ProgressBar]()
        self.ref_progress_txt = ft.Ref[ft.Text]()
        self.controls = [
            ft.Text(value='当前成功进度:'),
            ft.ProgressBar(
                value=0.0,
                width=400,
                color=ft.Colors.GREEN,
                bgcolor=ft.Colors.GREY,
                ref=self.ref_progress_bar
            ),
            ft.Text(ref=self.ref_progress_txt),
        ]

        self.ref_progress_txt.current.value = f'{self._current}/{self._total}'

        analysis_file_sig.connect(self.oe_analysis_file)
        scan_success_asig.connect(self.oe_scan_finish)
        start_scan_asig.connect(self.oe_start_scan)

    def clean_progress(self):
        self._total = 0
        self._current = 0

        self.ref_progress_bar.current.value = 0.0
        self.ref_progress_bar.current.update()

        self.ref_progress_txt.current.value = f'{self._current}/{self._total}'
        self.ref_progress_txt.current.update()

    def update_progress(self):
        self.ref_progress_bar.current.value = self._current/self._total
        self.ref_progress_bar.current.update()

        self.ref_progress_txt.current.value = f'{self._current}/{self._total}'
        self.ref_progress_txt.current.update()

    async def oe_start_scan(self, sender, **kw):
        self.clean_progress()

    async def oe_scan_finish(self, sender, **kw):
        self._current += 1
        self.update_progress()

    def oe_analysis_file(self, sender, **kw):
        files_path = kw.get('files_path')
        if files_path:
            self._total = len(files_path)
            self.update_progress()



@ft.control
class BottomAppBar(ft.BottomAppBar):

    def init(self):
        self.bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        self.content=CrawlerProgress()
