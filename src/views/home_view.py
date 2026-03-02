import flet as ft
from config import settings
from widgets import Error,Prompt
from utils.signals import start_scan_asig,update_settings_sig,show_matadata_asig,scan_failed_asig,organize_finished_asig
from schemas.movie import NfoMovieModel,NfoMovieTagModel,NfoMovieIntroductionModel,NfoMovieProductionModel
from core import state_manager
import asyncio
@ft.control
class SearchRow(ft.Row):
    expand : bool = True

    def init(self):
        self.ref_dir_tf = ft.Ref[ft.TextField]()
        self.ref_select_btn = ft.Ref[ft.Button]()
        self.ref_start_btn = ft.Ref[ft.Button]()
        self._select_dir = settings.select_dir or ""

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


    async def start(self, e):
        if not self._select_dir:
            self.page.show_dialog(Error("请先选择目录"))
            return

        await start_scan_asig.send_async('start_scan', path = self._select_dir)


@ft.control
class MetaInfo(ft.Container):
    expand : bool = True

    def init(self):
        self.ref_code = ft.Ref[ft.TextField]()
        self.ref_site = ft.Ref[ft.TextField]()
        self.ref_title = ft.Ref[ft.TextField]()
        self.ref_actor = ft.Ref[ft.TextField]()
        self.ref_tag = ft.Ref[ft.TextField]()
        self.ref_intro = ft.Ref[ft.TextField]()
        self.ref_director = ft.Ref[ft.TextField]()
        self.ref_maker = ft.Ref[ft.TextField]()
        self.ref_publisher = ft.Ref[ft.TextField]()

        self.rebuild()

        show_matadata_asig.connect(self.oe_update_meta)
        start_scan_asig.connect(self.rebuild)


    def rebuild(self):
        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=True,
                    controls=[
                        ft.TextField(label="番号",expand=1,ref=self.ref_code),
                        ft.TextField(label="网站",expand=2,ref=self.ref_site,read_only=True,on_click=self.launch_url),
                        ft.TextField(label='标题',expand=3,ref=self.ref_title),
                    ]
                ),
                ft.TextField(label='演员',expand=True,ref=self.ref_actor),
                ft.TextField(label='标签/类别',expand=True,ref=self.ref_tag),
                ft.TextField(label='简介', multiline=True,expand=True,ref=self.ref_intro),
                ft.Row(
                    expand=True,
                    controls=[
                        ft.TextField(label='导演',expand=True,ref=self.ref_director),
                        ft.TextField(label='制作商',expand=True,ref=self.ref_maker),
                        ft.TextField(label='发行商',expand=True,ref=self.ref_publisher),
                    ]
                ),
            ]
        )

    async def oe_update_meta(self, sender, **kw):
        metadata : NfoMovieModel = kw.get('metadata')
        if not metadata:
            return

        await self.show_metadata(metadata)


    async def show_metadata(self, metadata : NfoMovieModel):
        self.ref_code.current.value = metadata.num_code
        self.ref_site.current.value = metadata.website
        self.ref_title.current.value = metadata.title
        actors = metadata.actors
        if isinstance(actors, list):
            actor_name_list = [actor.name for actor in actors]
            self.ref_actor.current.value = ",".join(actor_name_list)
        tags : NfoMovieTagModel = metadata.tag_meta
        if tags:
            tag_list = []
            if tags.tag:
                tag_list.extend(tags.tag)
            if tags.genre:
                tag_list.extend(tags.genre)
            self.ref_tag.current.value = ",".join(tag_list)

        introduction_meta : NfoMovieIntroductionModel = metadata.introduction_meta
        if introduction_meta:
            self.ref_intro.current.value = introduction_meta.plot

        production_meta : NfoMovieProductionModel = metadata.production_meta
        if production_meta:
            self.ref_director.current.value = production_meta.director
            self.ref_maker.current.value = production_meta.studio
            self.ref_publisher.current.value = production_meta.publisher

        self.update()

    async def launch_url(self, e):
        await ft.UrlLauncher().launch_url(self.ref_site.current.value)


@ft.control
class CoverView(ft.Container):

    def init(self):
        self.expand = True
        self.ref_cover = ft.Ref[ft.Image]()
        self.ref_thumb = ft.Ref[ft.Image]()

        self.rebuild()

        show_matadata_asig.connect(self.oe_update_meta)

    def rebuild(self):
        self.content = ft.Row(
            expand=True,
            controls=[
                ft.Image(
                    src='src/assets/default_cover.jpg',
                    tooltip="封面",
                    expand=1,
                    ref=self.ref_cover,
                    error_content=ft.Text("封面加载失败")),
                ft.Image(
                    src='src/assets/default_tumb.jpg',
                    tooltip="缩略图",
                    expand=2,
                    ref=self.ref_thumb,
                    error_content=ft.Text("缩略图加载失败")),
            ]
        )



    async def oe_update_meta(self, sender, **kw):
        metadata : NfoMovieModel = kw.get('metadata')
        if not metadata:
            return

        await self.show_metadata_imgs(metadata)

    async def show_metadata_imgs(self, metadata : NfoMovieModel):

        imgs = metadata.imgs_meta
        if imgs:
            self.ref_cover.current.src = imgs.poster
            self.ref_thumb.current.src = imgs.thumb

        self.update()



@ft.control
class MainBody(ft.Container):
    expand : bool = True

    def init(self):

        self.content = ft.Column(
            expand=True,
            scroll= ft.ScrollMode.AUTO,
            controls=[
                SearchRow(),
                MetaInfo(),
                CoverView(),
            ]
        )


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

    def append_success(self, file_name : str):
        self.ref_success_et.current.controls.append(FileTile(file_name=file_name))
        self.ref_success_et.current.update()

    def append_fail(self, file_name : str):
        self.ref_fail_et.current.controls.append(FileTile(file_name=file_name,success=False))
        self.ref_fail_et.current.update()

    async def oe_scan_failed(self, sender, **kw):
        file_name : str = kw.get('failed_file')
        if file_name:
            self.append_fail(file_name)

    async def oe_organize_finished(self, sender, **kw):
        file_name : str = kw.get('file_name')
        if file_name:
            self.append_success(file_name)

@ft.control
class HomeView(ft.Container):
    expand : bool = True

    def init(self):
        self.content = ft.Row(
            expand=True,
            vertical_alignment  = ft.CrossAxisAlignment.START,
            controls=[
                MainBody(),
                SideInfoArea()
            ]
        )

    def build(self):
        self.page.appbar.title = "Home"





