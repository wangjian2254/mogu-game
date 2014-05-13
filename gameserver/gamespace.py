#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import logging
import uuid,json
from google.appengine.api import memcache
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'

gamespaceuserlist = 'appcode%sspace%suserlist'
gamespacelist = 'appcode%sspacelist'
spacestatus = 'space%s'
usergamepoint = 'appcode%sspace%susername%s'


def refreshSpace(appcode,spaceid):
    gslist = memcache.get(gamespacelist%(appcode))
    if not gslist:
        gslist = []
    if spaceid not in gslist:
        gslist.append(spaceid)
    else:
        return
    gslist = gslist[-20:]
    memcache.set(gamespacelist%(appcode),gslist,3600*24*3)

def createEmptySpace(appcode,spaceid=None,maxnum=6):
    if not spaceid:
        spaceid = str(uuid.uuid4())
    spacedict={'spaceid':spaceid, 'maxnum':maxnum, 'appcode':appcode, 'userlist':[], 'headlist':[], 'nicknamelist':[], 'pointlist':[], 'ranklist':[]}
    memcache.set(gamespaceuserlist%(appcode,spaceid),spacedict,3600*24)
    return spaceid,spacedict

class CreateSpace(Page):
    def get(self):
        username = self.request.get('username','')
        nickname = self.request.get('nickname','')
        head = self.request.get('head','')
        appcode = self.request.get('appcode','')
        maxnum = self.request.get('maxnum',0)

        spaceid = str(uuid.uuid4())
        from mogu.pointtool import getRankPointUsername
        point, rank = getRankPointUsername(appcode, username)
        spacedict={'spaceid':spaceid, 'maxnum':maxnum, 'author':username,'head':head,'appcode':appcode, 'userlist':[username], 'headlist':[head], 'nicknamelist':[nickname], 'pointlist':[point], 'ranklist':[rank]}
        memcache.set(gamespaceuserlist%(appcode,spaceid),spacedict,3600*24)
        refreshSpace(appcode,spaceid)

        self.flush(getResult(spaceid))

    def post(self):
        self.get()


class AddSpace(Page):

    def get(self):
        username = self.request.get('username','')
        nickname = self.request.get('nickname','')
        head = self.request.get('head','0')
        appcode = self.request.get('appcode','')
        spaceid = self.request.get('spaceid','')

        spacedict = memcache.get(gamespaceuserlist%(appcode,spaceid))
        # spaceid = str(uuid.uuid4())
        # spacedict={'spaceid':spaceid, 'author':username,'appcode':appcode, 'userlist':[username]}
        # memcache.set(gamespaceuserlist%(appcode,spaceid),spacedict,3600*24)

        if spacedict:
            if username not in spacedict.get('userlist',[]):
                from mogu.pointtool import getRankPointUsername
                point, rank = getRankPointUsername(appcode, username)
                spacedict['userlist'].append(username)
                spacedict['headlist'].append(head)
                spacedict['nicknamelist'].append(nickname)
                spacedict['pointlist'].append(point)
                spacedict['ranklist'].append(rank)
                memcache.set(gamespaceuserlist%(appcode,spaceid),spacedict,3600*24)
                refreshSpace(appcode,spaceid)
            self.flush(getResult(spacedict))
        else:
            self.flush(getResult(None,False,u'房间不存在'))



    def post(self):
        self.get()


class GetHotSpace(Page):
    def get(self):
        appcode = self.request.get('appcode','')
        start = int(self.request.get('start','0'))
        gslist = memcache.get(gamespacelist%(appcode))

        spacelist = []

        if gslist:
            for spaceid in gslist:
                spacedict =  memcache.get(gamespaceuserlist%(appcode,spaceid))
                if spacedict:
                    spacelist.append(spacedict)
        self.flush(getResult(spacelist))


    def post(self):
        self.get()


class GetSpace(Page):
    def get(self):
        appcode = self.request.get('appcode','')
        spaceid = self.request.get('spaceid','')


        spacedict =  memcache.get(gamespaceuserlist%(appcode,spaceid))
        if spacedict:
            self.flush(getResult(spacedict))
        else:
            self.flush(getResult(None,False,u'房间不存在'))


    def post(self):
        self.get()


class UploadPoint(Page):
    def get(self):
        username = self.request.get('username','')
        appcode = self.request.get('appcode','')
        spaceid = self.request.get('spaceid','')
        point = self.request.get('point','')

        logging.info("%s:%s:%s:%s"%(username,appcode,spaceid,point))

        memcache.set(usergamepoint%(appcode,spaceid,username),point,3600)
        spacedict = memcache.get(gamespaceuserlist%(appcode,spaceid))
        userpointdict = []
        if spacedict:
            for user in spacedict.get('userlist',[]):
                p = memcache.get(usergamepoint%(appcode,spaceid,user))
                userpointdict.append({'username':user, 'point':p})

        self.flush(getResult(userpointdict))

    def post(self):
        self.get()


class GetAllPoint(Page):
    def get(self):
        appcode = self.request.get('appcode','')
        spaceid = self.request.get('spaceid','')

        spacedict = memcache.get(gamespaceuserlist%(appcode,spaceid))
        userpointdict = []
        if spacedict:
            for user in spacedict.get('userlist',[]):
                p = memcache.get(usergamepoint%(appcode,spaceid,user))
                userpointdict.append({'username':user, 'point':p})
                logging.info("%s:%s:%s:%s"%(user,appcode,spaceid,p))

        self.flush(getResult(userpointdict))

    def post(self):
        self.get()

