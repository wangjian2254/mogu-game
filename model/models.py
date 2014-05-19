#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午9:21
import json
from google.appengine.api import memcache


__author__ = u'王健'

from google.appengine.ext import db

class Game(db.Model):
    model = db.StringProperty(indexed=False)

class Points(db.Model):
    '''
    key_name : appcode + ! + username
    '''
    # 假设用户对没有玩的游戏，失去兴趣了。
    #username = db.StringProperty() #用户名

    point = db.IntegerProperty() #游戏积分
    datetime = db.StringProperty(indexed=False)#积分时间



class Rank(db.Model):
    '''
    key_name: appcode
    积分对应的中文名称
    '''
    points = db.ListProperty(indexed=False,item_type=int)
    ranks = db.StringListProperty(indexed=False)


class RoomJson(db.Model):
    content = db.StringProperty(indexed=False)
    appcode = db.StringProperty()

    def get_spacedict(self):
        d = json.loads(self.content)
        from gameserver.gamespace import gamespaceuserlist
        memcache.set(gamespaceuserlist % (self.appcode, self.key().name()), d, 3600 * 24)
        return d

    @classmethod
    def get_spacedict_id(cls,id):
        from gameserver.gamespace import gamespaceuserlist
        d = memcache.get(gamespaceuserlist)
        if not d:
            rj = cls.get_by_key_name(id)
            d = rj.get_spacedict()
        return d


class Room(db.Model):
    '''
    key_name: appcode
    房间列表对应的中文名称
    '''
    num = db.IntegerProperty(indexed=False)#房间数量
    roomids = db.StringListProperty(indexed=False)

    def put(self, **kwargs):
        super(Room, self).put(**kwargs)
        from gameserver.gamespace import gamespacelist
        memcache.set(gamespacelist % (self.key().name()), self.roomids, 3600 * 24 * 3)

    @classmethod
    def get_spaceids(cls,appcode):
        from gameserver.gamespace import gamespacelist
        spaceids = memcache.get(gamespacelist % (appcode))
        if not spaceids:
            room = cls.get_by_key_name(appcode)
            memcache.set(gamespacelist % (room.key().name()), room.roomids, 3600 * 24 * 3)
            spaceids = room.roomids
        return spaceids