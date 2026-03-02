from blinker import Namespace

cmn_sig_namespace = Namespace()    # 通用信号

update_settings_sig = cmn_sig_namespace.signal('update_settings')
update_metadata_asig = cmn_sig_namespace.signal('update_metadata')


ui_sig_namespace = Namespace()     # 前端信号

nav_sig = ui_sig_namespace.signal('nav')
start_scan_asig = ui_sig_namespace.signal('start_scan')
clean_metainfo_sig = ui_sig_namespace.signal('clean_metainfo')

dir_settings_submit_sig = ui_sig_namespace.signal('dir_settings_changed')

be_sig_namespace = Namespace()      # 后端信号

download_progress_sig = be_sig_namespace.signal('download_progress')
download_finished_sig = be_sig_namespace.signal('download_finished')

scan_success_asig = be_sig_namespace.signal('scan_success')    # 搜刮成功
scan_failed_asig = be_sig_namespace.signal('scan_failed')    # 搜刮失败
scan_finished_asig = be_sig_namespace.signal('scan_finished')    # 搜刮完成
analysis_file_sig = be_sig_namespace.signal('analysis_file')    # 解析文件
scrape_finished_asig = be_sig_namespace.signal('scrape_finished')    # 爬虫完成
del_failed_file_asig = be_sig_namespace.signal('del_failed')    # 删除失败文件，第二次搜刮成功后删除原先失败的文件

organize_finished_asig = be_sig_namespace.signal('organize_finished')    # 整理完成,可以进行展示了
show_matadata_asig = be_sig_namespace.signal('show_metadata')    # 展示元数据
