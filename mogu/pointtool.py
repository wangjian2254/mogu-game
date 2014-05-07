#coding=utf-8
#author:u'王健'
#Date: 14-5-5
#Time: 下午8:21
from google.appengine.api import memcache

__author__ = u'王健'


from mogu.models import Points, Game, Rank

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

def getRankPoint(game):
    rank = memcache.get(game)
    if not rank:
        rank = Rank.get_by_key_name(game)
        if rank:
            memcache.set(game, rank, 3600 * 24 * 10)
        else:
            return None
    else:
        return rank


def getRankPointUsername(game, username):
    p = getPoint(game, username)
    r = getRankPoint(game)
    point = 0
    rank = ''
    if p:
        point = p.point
    if r:
        for i,n in enumerate(r.points):
            if point <= n:
                rank = r.ranks[i]
    return point, rank

