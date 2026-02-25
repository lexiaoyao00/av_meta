import flet as ft
from config import settings
from widgets import Error
from utils.signals import start_scan_sig,update_settings_sig,show_matadata_sig,scrape_finished_sig
from schemas.movie import NfoMovieModel,NfoMovieTagModel,NfoMovieIntroductionModel,NfoMovieProductionModel
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


    async def start(self, e):
        if not self._select_dir:
            self.page.show_dialog(Error("请先选择目录"))
            return

        await start_scan_sig.send_async('start_scan', path = self._select_dir)


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

    def build(self):
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

    async def update_meta(self, sender, **kw):
        metadata : NfoMovieModel = kw.get('metadata')
        if not metadata:
            return
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



    def build(self):
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

    async def update_meta(self, sender, **kw):
        metadata : NfoMovieModel = kw.get('metadata')
        if not metadata:
            return

        imgs = metadata.imgs_meta
        if imgs:
            self.ref_cover.current.src = imgs.poster
            self.ref_thumb.current.src = imgs.thumb

        self.update()



@ft.control
class HomeView(ft.Container):
    expand : bool = True

    def init(self):
        self.search_row = SearchRow()
        self.meta_info = MetaInfo()
        self.cover_view = CoverView()




    def build(self):
        self.page.appbar.title = "Home"
        self.content = ft.Column(
            expand=True,
            scroll= ft.ScrollMode.AUTO,
            controls=[
                self.search_row,
                self.meta_info,
                self.cover_view,
            ]
        )

        show_matadata_sig.connect(self.meta_info.update_meta)
        show_matadata_sig.connect(self.cover_view.update_meta)

    def show_meta(self):
        ...