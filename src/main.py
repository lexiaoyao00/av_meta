import flet as ft
from widgets import NavDrawer,AppBar
from utils.signals import nav_sig
from views import HomeView, SettingsView
from config import save_current_settings
import sys
from core.controller import Controller


NAV_ROUTES = {
    0: HomeView(),
    1: SettingsView(),
}



def main(page: ft.Page):
    controller = Controller()
    page.scroll = ft.ScrollMode.AUTO

    body_content = HomeView()

    def oe_nav_by_index(sender,**kw):
        idx = kw.get('index')
        content = NAV_ROUTES.get(idx)
        if not content:
            raise Exception("未知的导航索引")

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
    page.add(body_content)





if __name__ == "__main__":
    ft.run(main)