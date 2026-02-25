from blinker import Namespace

cmn_sig_namespace = Namespace()    # 通用信号

update_settings_sig = cmn_sig_namespace.signal('update_settings')
update_metadata_sig = cmn_sig_namespace.signal('update_metadata')


ui_sig_namespace = Namespace()     # 前端信号

nav_sig = ui_sig_namespace.signal('nav')
start_scan_sig = ui_sig_namespace.signal('start_scan')

be_sig_namespace = Namespace()      # 后端信号

download_progress_sig = be_sig_namespace.signal('download_progress')
download_finished_sig = be_sig_namespace.signal('download_finished')

scan_failed_sig = be_sig_namespace.signal('scan_failed')    # 搜刮失败
analysis_file_sig = be_sig_namespace.signal('analysis_file')    # 解析文件
scrape_finished_sig = be_sig_namespace.signal('scrape_finished')    # 爬虫完成

show_matadata_sig = be_sig_namespace.signal('show_metadata')    # 展示元数据
