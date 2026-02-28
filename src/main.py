import flet as ft
from widgets import NavDrawer,AppBar
from utils.signals import nav_sig
from views import HomeView, SettingsView
from config import save_current_settings
import sys
from core.controller import Controller
from loguru import logger
from config import settings
from pathlib import Path


NAV_ROUTES = {
    0: HomeView(),
    1: SettingsView(),
}

def log_init():
    log_dir_path = Path(settings.log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)
    # logger.remove()
    logger.add(log_dir_path / "info.log", rotation="5 MB", level="INFO")
    # logger.info("日志初始化成功")


def main(page: ft.Page):
    log_init()
    controller = Controller()
    page.scroll = ft.ScrollMode.AUTO

    body_content = HomeView()

    def oe_nav_by_index(sender,**kw):
        idx = kw.get('index')
        content = NAV_ROUTES.get(idx)
        if not content:
            raise Exception("未知的导航索引")
        # if idx == 1:
        #     page.floating_action_button.visible = True
        # else:
        #     page.floating_action_button.visible = False
        body_content.content = content
        body_content.update()


    nav_sig.connect(oe_nav_by_index,'nav_drawer',False)

    async def on_close(e):
        save_current_settings()
        await page.window.destroy()
        sys.exit(0)

    page.on_close = on_close

    page.appbar = AppBar()
    page.drawer = NavDrawer()
    # page.floating_action_button = ft.FloatingActionButton('保存',visible=False)
    page.add(body_content)





if __name__ == "__main__":
    ft.run(main)