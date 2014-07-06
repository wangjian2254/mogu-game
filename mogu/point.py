#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午11:25
import datetime
import logging

from google.appengine.api import memcache

from model.models import Points, Game
from mogu.pointtool import keystr, getPoint, getRankPointUsername
from tools.page import Page
from tools.util import getResult


__author__ = u'王健'

timezone = datetime.timedelta(hours=8)
timeformate = "%Y-%m-%d %H:%M:%S"
timeformateday = "%Y-%m-%d"
timeformatemonth = "%Y-%m"




def setPoint(game, username, point,datetimestr,model):
    point = int(point)
    key = keystr % (game, username)
    nowdate = datetime.datetime.utcnow() + timezone
    nowdate.isocalendar()
    nowdate.isoweekday()
    uploaddate = datetime.datetime.strptime(datetimestr,timeformate)
    p = getPoint(game, username)
    if not p:
        p = Points(key_name=key)
        p.point = int(point)
        p.datetime = datetimestr
        p.put()
    else:
        if model == 'daily':
            n=nowdate.strftime(timeformateday)
            u=uploaddate.strftime(timeformateday)
            if n == u:
                if p.datetime.splite(' ')[0]==u:
                    if p.point<point:
                        p.point=point
                        p.put()
                elif p.datetime.splite(' ')[0]<u:
                    p.point=point
                    p.datetime = datetimestr
                    p.put()
        elif model == 'weekly':
            if nowdate.isocalendar()[1]==uploaddate.isocalendar()[1]:
                if datetime.datetime.strptime(p.datetime,timeformate).isocalendar()[1]==nowdate.isocalendar()[1]:
                    if p.point<point:
                        p.point=point
                        p.put()
                elif datetime.datetime.strptime(p.datetime,timeformate).isocalendar()[1]<nowdate.isocalendar()[1]:
                    p.point=point
                    p.datetime = datetimestr
                    p.put()
        elif model == 'monthly':
            n=nowdate.strftime(timeformatemonth)
            u=uploaddate.strftime(timeformatemonth)
            if n==u:
                if p.datetime[:7]==n:
                    if p.point<point:
                        p.point=point
                        p.put()
                elif p.datetime[:7]<n:
                    p.point=point
                    p.datetime = datetimestr
                    p.put()


        elif model == 'year':
            if nowdate.year==uploaddate.year:
                if p.datetime[:4]==str(nowdate.year):
                    if p.point<point:
                        p.point=point
                        p.put()
                elif p.datetime[:4]<str(nowdate.year):
                    p.point=point
                    p.datetime = datetimestr
                    p.put()

        else:
            p.point += int(point)
            p.datetime = datetimestr
            p.put()
    memcache.set(key, p, 3600 * 24 * 7)
    return p

def getGame(code):
    p = memcache.get(code)
    if not p:
        p = Game.get_by_key_name(code)
        if p:
            memcache.set(code, p, 3600 * 24 * 7)
            return p
        else:
            return None
    else:
        return p
def setGame(code,model):
    p = getGame(code)
    if not p:
        p = Game(key_name=code)
        p.model = model
        p.put()
    else:
        if p.model != model:
            p.model = model
            p.put()
    return p

class PointUpdate(Page):

    def get(self):
        self.post()

    def post(self):
        try:
            username = self.request.get('UserName')
            game = self.request.get('game')
            point = self.request.get('point')
            datetime = self.request.get('datetime')
            model = self.request.get('model')
            g = setGame(game,model)
            #logging.error("game",'%s_%s_%s_%s_%s'%(game,username,point,datetime,model))
            p=setPoint(game, username, point,datetime,model)
            self.flush(getResult(p.point))
        except Exception,e:
            logging.error("pointupdate "+str(e))
            self.flush(getResult(False, False, u'保存积分失败。'))


def sortedpoint(p):
    return p.point


class PointQuery(Page):
    '''
    用来查询，用来查询游戏的积分，并且排序。
    '''
    def post(self):
        '''
        查询并输出而且排序
        '''
        result = {'list':[],'my':None,'game':None}
        try:

            user = self.request.get('UserName')
            game = self.request.get('game')
            key = keystr % (game, user)
            result['game'] = game
            g = getGame(game)
            result['model'] = g.model
            userlist = self.request.get('userlist', '').split(',')

            pointlist = []
            for username in userlist:
                if username:
                    p= getPoint(game, username)
                    if p:
                        pointlist.append(p)
            pointlist = sorted(pointlist, key=sortedpoint)
            for i,p in enumerate(pointlist):
                if p.key().name() == key:
                    result['my'] = i+1
                result['list'].append({'username':p.key().name().split('!')[1], 'point':p.point, 'datetime':p.datetime})

            self.flush(getResult(result,message=u'积分记录查询成功'))
        except Exception,e:
            self.flush(getResult(False, False, u'积分记录查询失败。'))


class UserPointQuery(Page):
    '''
    用来查询，用来查询游戏的积分，并且排序。
    '''
    def post(self):
        '''
        查询并输出而且排序
        '''
        result = []
        try:

            user = self.request.get('UserName')
            gamelist = self.request.get('gamelist', '').split(',')
            for game in gamelist:
                p,r,t=getRankPointUsername(game, user)
                result.append({'username':user, 'point':p,'rank':r, 'game':game, 'datetime':t})
            self.flush(getResult(result,message=u'积分记录查询成功'))
        except:
            self.flush(getResult(False, False, u'积分记录查询失败。'))


def sortedgamepoint(p):
    return p[1]

class PointOnceUpdate(Page):

    def get(self):
        self.post()

    def post(self):
        result = []
        try:
            num = int(self.request.get('num','0'))
            game = self.request.get('game')
            nowdate = (datetime.datetime.utcnow() + timezone).strftime(timeformate)
            l = []
            for i in range(num):
                username = self.request.get('username%s'%i)
                point = self.request.get('point%s'%i)
                l.append((username,point))
            l = sorted(l, key=sortedgamepoint)
            f_s = len(l)/2
            f_c = len(l)%2
            for username,point in l:
                if f_s==0 and not f_c :
                    f_s-=1
                setPoint(game, username, f_s,nowdate,'')
                f_s-=1
                p,r,t=getRankPointUsername(game, username)
                result.append({'u':username, 'p':p,'r':r})
            self.flush(getResult(result,message=u'积分记录查询成功'))
        except Exception,e:
            logging.error("pointupdate "+str(e))
            self.flush(getResult(False, False, u'保存积分失败。'))
