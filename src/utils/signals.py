from blinker import Namespace

cmn_sig_namespace = Namespace()    # 通用信号

update_settings_sig = cmn_sig_namespace.signal('update_settings')


ui_sig_namespace = Namespace()     # 前端信号

nav_sig = ui_sig_namespace.signal('nav')
start_scan_sig = ui_sig_namespace.signal('start_scan')

be_sig_namespace = Namespace()      # 后端信号

download_progress_sig = be_sig_namespace.signal('download_progress')
