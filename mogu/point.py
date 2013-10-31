#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午11:25
import datetime
from google.appengine.api import memcache
from mogu.models.model import Points
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'

timezone = datetime.timedelta(hours=8)

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


def setPoint(game, username, point):
    key = keystr % (game, username)
    p = getPoint(game, username)
    if not p:
        p = Points(key_name=key)
        p.point = int(point)
        #p.username = username
        p.put()
    else:
        p.point += int(point)
        p.put()
    memcache.set(key, p, 3600 * 24 * 7)
    return p


class PointUpdate(Page):
    def post(self):
        try:
            username = self.request.get('UserName')
            game = self.request.get('game')
            point = self.request.get('point')

            p=setPoint(game, username, point)
            self.flush(getResult(p.point))
        except:
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
            userlist = self.request.get('userlist', '').split(',')

            pointlist = []
            for username in userlist:
                if username:
                    pointlist.append(getPoint(game, username))
            pointlist = sorted(pointlist, key=sortedpoint)
            for i,p in enumerate(pointlist):
                if p.key().name() == key:
                    result['my'] = i+1
                result['list'].append({'username':p.key().name().split('!')[1:], 'point':p.point,'game':game})

            self.flush(getResult(result,message=u'积分记录查询成功'))
        except:
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
                p=getPoint(game, user)
                result.append({'username':user, 'point':p.point,'game':game})
            self.flush(getResult(result,message=u'积分记录查询成功'))
        except:
            self.flush(getResult(False, False, u'积分记录查询失败。'))

