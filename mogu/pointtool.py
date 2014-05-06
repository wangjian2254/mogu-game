#coding=utf-8
#author:u'王健'
#Date: 14-5-5
#Time: 下午8:21
from google.appengine.api import memcache

__author__ = u'王健'


from mogu.models import Points, Game

keystr = '%s!%s'
def getPoint(game, username):
    key = keystr % (game, username)
    p = memcache.get(key)
    if not p:
        p = Points.get_by_key_name(key)
        if p:
            memcache.set(key, p, 3600 * 24 * 7)
            return p
        else:
            return None
    else:
        return p
  