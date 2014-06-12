#coding=utf-8
#author:u'王健'
#Date: 14-5-5
#Time: 下午9:00
import json
import uuid
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


class RoomCreate(Page):
    def get(self):
        appcode = self.request.get('appcode', '')
        if appcode:
            room = Room.get_by_key_name(appcode)

        else:
            room = None

        self.render('template/room/roomUpdate.html', {'room': room, 'pluginurl': WEBURL, 'appcode':appcode})

    def post(self):
        appcode = self.request.get('appcode', None)
        num = self.request.get('num', 20)
        if appcode:
            room = Room.get_by_key_name(appcode)
            if not room:
                room = Room(key_name=appcode)
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


            self.render('template/room/roomUpdate.html', {'room': room, 'pluginurl': WEBURL, 'appcode':appcode, 'result':'succeed', 'msg':u'保存成功'})
        else:
            self.render('template/room/roomUpdate.html', {'room': None, 'pluginurl': WEBURL, 'appcode':appcode, 'result':'warning', 'msg':u'应用包名不存在'})


class RoomDelete(Page):
    def get(self):
        appcode = self.request.get('appcode', None)
        if appcode:
            room = Room.get_by_key_name(appcode)
            room.delete()
        self.flush(getResult(appcode, True, u'删除成功'))