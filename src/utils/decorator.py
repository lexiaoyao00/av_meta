import threading
from functools import wraps

def singleton(cls):
    """
    线程安全的单例模式装饰器
    """
    instances = {}
    lock = threading.Lock()

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                # 双重检查，保证多线程安全
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
