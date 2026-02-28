import flet as ft
from utils.signals import dir_settings_submit_sig

@ft.control
class DirBrowser(ft.Row):

    def __init__(self,val : str, label: str = None, **kwargs):
        self.text_val = val
        self.text_label = label
        self.ref_tf = ft.Ref[ft.TextField]()
        super().__init__(**kwargs)


    def init(self):
        self.expand = True


    def build(self):
        self.controls = [
            ft.IconButton(icon=ft.Icons.FOLDER_OPEN, on_click=self._on_click),
            ft.TextField(
                label= self.text_label,
                value= self.text_val,
                width= 500,
                ref= self.ref_tf,
                on_submit= self._on_submit,
            ),
        ]

    def _on_submit(self,e:ft.Event[ft.TextField]):
        self.text_val = e.control.value
        dir_settings_submit_sig.send(self.text_label, value=self.text_val)

    async def _on_click(self,e:ft.Event[ft.IconButton]):
        dir = await ft.FilePicker().get_directory_path()
        # print(dir)
        if dir:
            self.text_val = dir
            self.ref_tf.current.value = self.text_val
            self.ref_tf.current.update()
            dir_settings_submit_sig.send(self.text_label, value=self.text_val)
