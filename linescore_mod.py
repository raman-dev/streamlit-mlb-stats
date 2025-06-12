import diskcache
import functools
from dataclasses import dataclass,asdict

class MyClassDecorator:
    def __init__(self,func):
        self.func = func

    def __call__(self,*args,**kwargs):
        print("Calling .__call__()")
        kwargs['name']="Decorated.Name"
        r = self.func(*args,**kwargs)
        return r

@MyClassDecorator
@dataclass
class MyClass:
    name: str
    val: int

CACHE_DIR = "statsapi_cache"

def cacheit(key_prefix="",keys=[]):
    # print("Decorating...")
    def decorator(func):
        # print("Calling cacheit.decorator")
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
        #     cache_key = key_prefix
        #     for k in keys:
        #         cache_key += "_" + kwargs[k]

        #     print("Cache key => ",cache_key)
            #check cache for key
            result = func(*args,**kwargs)
            return result
        return wrapper
    return decorator

@cacheit(key_prefix="linescore",keys=["gameId"])
@dataclass
class Linescore:
    gameId: int
    linescoreData: dict

