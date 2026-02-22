from blinker import Namespace

cmn_sig_namespace = Namespace()

update_settings_sig = cmn_sig_namespace.signal('update_settings')


ui_sig_namespace = Namespace()

nav_sig = ui_sig_namespace.signal('nav')
start_scan_sig = ui_sig_namespace.signal('start_scan')