import socket
import requests
from time import time

def GetJSON():
    return requests.get('http://www.watchpeoplecode.com/json').json()

def JSONtoSet(jsonObject):
    li = set()
    for obj in jsonObject['upcoming']:
        li.add(obj['title'])
    return li

lastTime = time()
cacheLiveStreams = GetJSON()
newCacheLiveStreams = cacheLiveStreams

if time() >= lastTime + 3:
    lastTime = time()
    newCacheStreams = JSONtoSet(GetJSON())
    cacheCheck = newCacheStreams - cacheLiveStreams
    if cacheCheck:
        print(cacheCheck)
    cacheLiveStreams = newCacheStreams
