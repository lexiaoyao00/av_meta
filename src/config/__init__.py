__all__ = [
    'settings',
    'save_current_settings',
    'PRO_PATH',
]

from .app_settings import load_config, PRO_PATH,save_settings

settings = load_config()

def save_current_settings():
    save_settings(settings)


from utils.signals import update_settings_sig
def oe_update_settings(sender,**kw):
    field:str = kw.get('field','no_set_field')
    value = kw.get('value')
    settings.update_field(field, value)

update_settings_sig.connect(oe_update_settings)