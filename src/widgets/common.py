import flet as ft

@ft.control
class DirBrowser(ft.Row):

    def __init__(self,val : str, label: str = None, ):
        self.text_val = val
        self.text_label = label
        self.ref_tf = ft.Ref[ft.TextField]()

        super().__init__()


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
            ),
        ]

    async def _on_click(self,e:ft.Event[ft.IconButton]):
        dir = await ft.FilePicker().get_directory_path()
        # print(dir)
        self.text_val = dir
        self.ref_tf.current.value = self.text_val
        self.ref_tf.current.update()
