#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import logging
import uuid, json
from google.appengine.api import memcache
from mogu.pointtool import getRoomNum
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'

gamespaceuserlist = 'userlist_appcode%sspace%suserlist'
gamespacelist = 'spacelist_appcode%sspacelist'
spacestatus = 'space%s'
usergamepoint = 'point_appcode%sspace%susername%s'
usercurrentroom = 'room_appcode%ssername%s'

gameflushnum = 18


def refreshSpace(appcode, spaceid):
    gslist = memcache.get(gamespacelist % (appcode))
    if not gslist:
        gslist = []
    if spaceid not in gslist:
        gslist.append(spaceid)
    else:
        return
    memcache.set(gamespacelist % (appcode), gslist, 3600 * 24 * 3)


def createEmptySpace(appcode, spaceid=None, maxnum=6,index=0):
    if not spaceid:
        spaceid = str(uuid.uuid4())
    spacedict = {'spaceid': spaceid, 'roomname':u'房间 %s'%index, 'maxnum': maxnum, 'appcode': appcode, 'userlist': [], 'headlist': [],
                 'nicknamelist': [], 'pointlist': [], 'ranklist': []}
    memcache.set(gamespaceuserlist % (appcode, spaceid), spacedict, 3600 * 24)
    return spaceid, spacedict

def quitSpaceRoom(appcode,spaceid,username):
    spacedict = memcache.get(gamespaceuserlist % (appcode, spaceid))
    if spacedict and username in spacedict.get('userlist', []):
        index = spacedict['userlist'].index(username)
        spacedict['userlist'].pop(index)
        spacedict['headlist'].pop(index)
        spacedict['nicknamelist'].pop(index)
        spacedict['pointlist'].pop(index)
        spacedict['ranklist'].pop(index)
        memcache.set(gamespaceuserlist % (appcode, spaceid), spacedict, 3600 * 24)

def userCurrentRoom(appcode,sid,username):
    spaceid = memcache.get(usercurrentroom % (appcode,username))
    if sid!=spaceid and spaceid:
        quitSpaceRoom(appcode,spaceid,username)
    elif not spaceid:
        memcache.set(usercurrentroom % (appcode,username),sid,3600*24)



class CreateSpace0(Page):
    def get(self):
        username = self.request.get('username', '')
        nickname = self.request.get('nickname', '')
        head = self.request.get('head', '')
        appcode = self.request.get('appcode', '')
        maxnum = self.request.get('maxnum', 0)

        from mogu.pointtool import getRankPointUsername

        point, rank = getRankPointUsername(appcode, username)
        spaceid, spacedict = createEmptySpace(appcode, index=1)
        spacedict['userlist'].append(username)
        spacedict['headlist'].append(head)
        spacedict['nicknamelist'].append(nickname)
        spacedict['pointlist'].append(point)
        spacedict['ranklist'].append(rank)
        memcache.set(gamespaceuserlist % (appcode, spaceid), spacedict, 3600 * 24)
        refreshSpace(appcode, spaceid)

        self.flush(getResult(spaceid))

    def post(self):
        self.get()


class CreateSpace(Page):
    def get(self):
        username = self.request.get('username', '')
        nickname = self.request.get('nickname', '')
        head = self.request.get('head', '')
        appcode = self.request.get('appcode', '')
        maxnum = self.request.get('maxnum', 6)

        sid = None
        from mogu.pointtool import getRankPointUsername

        point, rank = getRankPointUsername(appcode, username)

        gslist = memcache.get(gamespacelist % (appcode))
        if not gslist:
            gslist = []
        for spaceid in gslist:
            spacedict = memcache.get(gamespaceuserlist % (appcode, spaceid))
            if spacedict and spacedict.get('status', 0) == 0 and len(spacedict.get('userlist', [])) < spacedict.get(
                    'maxnum', 6) and username not in spacedict.get('userlist', []):
                point, rank = getRankPointUsername(appcode, username)
                spacedict['userlist'].append(username)
                spacedict['headlist'].append(head)
                spacedict['nicknamelist'].append(nickname)
                spacedict['pointlist'].append(point)
                spacedict['ranklist'].append(rank)
                memcache.set(gamespaceuserlist % (appcode, spaceid), spacedict, 3600 * 24)
                sid = spaceid
                break
        if not sid and len(gslist) == 0:
            sid, spacedict = createEmptySpace(appcode, index=1)
            spacedict['userlist'].append(username)
            spacedict['headlist'].append(head)
            spacedict['nicknamelist'].append(nickname)
            spacedict['pointlist'].append(point)
            spacedict['ranklist'].append(rank)


            memcache.set(gamespaceuserlist % (appcode, sid), spacedict, 3600 * 24)
            refreshSpace(appcode, sid)
        userCurrentRoom(appcode,sid,username)
        self.flush(getResult(sid))

    def post(self):
        self.get()


class AddSpace(Page):
    def get(self):
        username = self.request.get('username', '')
        nickname = self.request.get('nickname', '')
        head = self.request.get('head', '0')
        appcode = self.request.get('appcode', '')
        spaceid = self.request.get('spaceid', '')

        spacedict = memcache.get(gamespaceuserlist % (appcode, spaceid))
        # spaceid = str(uuid.uuid4())
        # spacedict={'spaceid':spaceid, 'author':username,'appcode':appcode, 'userlist':[username]}
        # memcache.set(gamespaceuserlist%(appcode,spaceid),spacedict,3600*24)

        if spacedict and spacedict.get('status', 0) == 0 and len(spacedict.get('userlist', [])) < spacedict.get(
                'maxnum', 6) and username not in spacedict.get('userlist', []):
            from mogu.pointtool import getRankPointUsername

            point, rank = getRankPointUsername(appcode, username)
            spacedict['userlist'].append(username)
            spacedict['headlist'].append(head)
            spacedict['nicknamelist'].append(nickname)
            spacedict['pointlist'].append(point)
            spacedict['ranklist'].append(rank)
            memcache.set(gamespaceuserlist % (appcode, spaceid), spacedict, 3600 * 24)
            userCurrentRoom(appcode,spaceid,username)
            self.flush(getResult(spaceid))
        elif spacedict.get('status', 0) == 1:
            self.flush(getResult(None, False, u'玩家正在游戏，不能加入'))
        elif len(spacedict.get('userlist', [])) >= spacedict.get('maxnum', 6):
            self.flush(getResult(None, False, u'玩家已经满员，不能加入'))
        elif username in spacedict.get('userlist', []):
            self.flush(getResult(spaceid))
        else:
            self.flush(getResult(None, False, u'房间已经不存在，请刷新房间列表'))


    def post(self):
        self.get()


class QuiteSpace(Page):
    def get(self):
        username = self.request.get('username', '')

        appcode = self.request.get('appcode', '')
        spaceid = self.request.get('spaceid', '')

        spacedict = memcache.get(gamespaceuserlist % (appcode, spaceid))
        if spacedict and username in spacedict.get('userlist', []):
            quitSpaceRoom(appcode,spaceid,username)
        elif username not in spacedict.get('userlist', []):
            self.flush(getResult(True, True, u'用户不在房间'))
        else:
            self.flush(getResult(None, False, u'房间已经不存在，请刷新房间列表'))


    def post(self):
        self.get()


class GetHotSpace(Page):
    def get(self):
        appcode = self.request.get('appcode', '')
        start = int(self.request.get('start', '0'))
        gslist = memcache.get(gamespacelist % (appcode))
        if not gslist:
            gslist = []
        spacelist = []
        num=start+1
        for spaceid in gslist[start:start + gameflushnum]:
            spacedict = memcache.get(gamespaceuserlist % (appcode, spaceid))
            if not spacedict:
                spaceid, spacedict = createEmptySpace(appcode, spaceid,index=num)
            spacelist.append(spacedict)
            num+=1
        roomnum = getRoomNum(appcode)
        if len(gslist) < roomnum:
            for i in range(roomnum - len(gslist)):
                spaceid, spacedict = createEmptySpace(appcode,index=i+1)
                refreshSpace(appcode, spaceid)
                if len(spacelist) < gameflushnum:
                    spacelist.append(spacedict)
        self.flush(getResult(spacelist))


    def post(self):
        self.get()


class GetSpace(Page):
    def get(self):
        appcode = self.request.get('appcode', '')
        spaceid = self.request.get('spaceid', '')

        spacedict = memcache.get(gamespaceuserlist % (appcode, spaceid))
        if spacedict:
            self.flush(getResult(spacedict))
        else:
            self.flush(getResult(None, False, u'房间不存在'))


    def post(self):
        self.get()


class UploadPoint(Page):
    def get(self):
        username = self.request.get('username', '')
        appcode = self.request.get('appcode', '')
        spaceid = self.request.get('spaceid', '')
        point = self.request.get('point', '')

        logging.info("%s:%s:%s:%s" % (username, appcode, spaceid, point))

        memcache.set(usergamepoint % (appcode, spaceid, username), point, 3600)
        spacedict = memcache.get(gamespaceuserlist % (appcode, spaceid))
        userpointdict = []
        if spacedict:
            for user in spacedict.get('userlist', []):
                p = memcache.get(usergamepoint % (appcode, spaceid, user))
                userpointdict.append({'username': user, 'point': p})

        self.flush(getResult(userpointdict))

    def post(self):
        self.get()


class GetAllPoint(Page):
    def get(self):
        appcode = self.request.get('appcode', '')
        spaceid = self.request.get('spaceid', '')

        spacedict = memcache.get(gamespaceuserlist % (appcode, spaceid))
        userpointdict = []
        if spacedict:
            for user in spacedict.get('userlist', []):
                p = memcache.get(usergamepoint % (appcode, spaceid, user))
                userpointdict.append({'username': user, 'point': p})
                logging.info("%s:%s:%s:%s" % (user, appcode, spaceid, p))

        self.flush(getResult(userpointdict))

    def post(self):
        self.get()

