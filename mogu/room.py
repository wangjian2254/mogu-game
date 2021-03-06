#coding=utf-8
#author:u'王健'
#Date: 14-5-5
#Time: 下午9:00
import json
import uuid
from google.appengine.api import memcache
from model.models import Room, RoomJson
from setting import WEBURL
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'


class RoomList(Page):
    def get(self):
        start = 0
        appcode = self.request.get('appcode', None)
        if appcode:
            room = Room.get_by_key_name(appcode)
            if room:
                roomlist = [room]
            else:
                roomlist = []
        else:
            start = int(self.request.get('start', '0'))
            roomlist = Room.all().order('-__key__').fetch(20, start)
        pre = start - 20
        if pre < 0:
            pre = 0
        nex = start + 20
        self.render('template/room/roomList.html',
                    {'roomlist': roomlist, 'pre': pre, 'nex': nex, 'limit': 20, 'count': len(roomlist),
                     'pluginurl': WEBURL, 'appcode':appcode})

    def post(self):
        return self.get()


class RoomPluginList(Page):
    def get(self):
        cachename = 'roomlist'
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        l = []
        for r in Room.all().order('-__key__'):
            l.append(r.id)
        self.getResult(True, u'', ','.join(l), cachename=cachename)

class RoomCreate(Page):
    def get(self):
        appcode = self.request.get('appcode', '')
        cachename = 'roomlist_%s' % appcode
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        if appcode:
            room = Room.get_by_key_name(appcode)
        else:
            room = None
        if room:
            self.getResult(True, u'获取房间信息成功', {"appcode": appcode, 'roomnum': room.num},cachename=cachename)
        else:
            self.getResult(True, u'获取房间信息成功', {"appcode": appcode, 'roomnum': 0},cachename=cachename)
        # self.render('template/room/roomUpdate.html', {'room': room, 'pluginurl': WEBURL, 'appcode':appcode})

    def post(self):
        appcode = self.request.get('appcode', None)
        id = self.request.get('id', None)
        cachename = 'roomlist_%s' % appcode
        memcache.delete(cachename)
        num = self.request.get('num', 20)
        if appcode:
            room = Room.get_by_key_name(appcode)
            if not room:
                room = Room(key_name=appcode)
                room.id = id
                memcache.delete( 'roomlist')
            room.num = int(num)

            for i in range(room.num-len(room.roomids)):
                spid = 'room'+str(uuid.uuid4())
                room.roomids.append(spid)
                roomjson = RoomJson(key_name=spid)
                from gameserver.gamespace import createEmptySpace
                spid,spacedict = createEmptySpace(appcode,spid,6,len(room.roomids))
                roomjson.appcode=appcode
                roomjson.content = json.dumps(spacedict)
                roomjson.put()

            room.put()


            self.getResult(True, u'保存房间设置成功', None)
            # self.render('template/room/roomUpdate.html', {'room': room, 'pluginurl': WEBURL, 'appcode':appcode, 'result':'succeed', 'msg':u'保存成功'})
        else:
            self.getResult(False, u'应用包名不存在', None)
            # self.render('template/room/roomUpdate.html', {'room': None, 'pluginurl': WEBURL, 'appcode':appcode, 'result':'warning', 'msg':u'应用包名不存在'})


class RoomDelete(Page):
    def get(self):
        appcode = self.request.get('appcode', None)
        if appcode:
            room = Room.get_by_key_name(appcode)
            room.delete()
        self.flush(getResult(appcode, True, u'删除成功'))

class RoomJSONFile(Page):
    def get(self):
        appcode = self.request.get('appcode')
        if appcode:
            room = Room.get_by_key_name(appcode)
            if room:
                r={'appcode':room.key().name(),'roomlist':[]}
                for rid in room.roomids:
                    roomdict = RoomJson.get_spacedict_id(room.key().name(),rid)
                    del roomdict['userlist']
                    del roomdict['headlist']
                    del roomdict['nicknamelist']
                    del roomdict['pointlist']
                    del roomdict['ranklist']
                    del roomdict['appcode']
                    r['roomlist'].append(roomdict)
                self.flush(r)
            else:
                self.error(400)
        else:
            rl = []
            for room in Room.all():
                r={'appcode':room.key().name(),'roomlist':[]}
                for rid in room.roomids:
                    roomdict = RoomJson.get_spacedict_id(room.key().name(),rid)
                    del roomdict['userlist']
                    del roomdict['headlist']
                    del roomdict['nicknamelist']
                    del roomdict['pointlist']
                    del roomdict['ranklist']
                    del roomdict['appcode']
                    r['roomlist'].append(roomdict)
                rl.append(r)
            self.flush({'gamelist':rl})
