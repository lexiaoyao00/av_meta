import flet as ft



@ft.control
class Alert(ft.AlertDialog):
    def __init__(self, msg : str):
        self._msg = msg or ""
        super().__init__()

    def build(self):
        self.content = ft.Text(self._msg)

@ft.control
class Prompt(Alert):
    def __init__(self, msg : str):
        super().__init__(msg)

    def init(self):
        self.title = ft.Text("提示")




@ft.control
class Warning(Alert):
    def __init__(self, msg : str):
        super().__init__(msg)

    def init(self):
        self.title = ft.Text("警告")



@ft.control
class Error(Alert):
    def __init__(self, msg : str):
        super().__init__(msg)

    def init(self):
        self.title = ft.Text("错误")