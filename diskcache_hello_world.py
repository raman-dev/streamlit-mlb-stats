from diskcache import Cache

# cache = Cache() expects a directory path param if none creates temporary directory

with Cache("hello_world_cache") as reference:
    reference.set('hello','world')


with Cache("hello_world_cache") as refernece:
    print(reference.get('hello'),'read from cache')