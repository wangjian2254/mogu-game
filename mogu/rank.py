# coding=utf-8
# author:u'王健'
#Date: 14-5-5
#Time: 下午9:00
from google.appengine.api import memcache
from model.models import Rank
from setting import WEBURL
from tools.page import Page
from tools.util import getResult

__author__ = u'王健'


class RankList(Page):
    def get(self):
        start = 0
        appcode = self.request.get('appcode', None)
        if appcode:
            rank = Rank.get_by_key_name(appcode)
            if rank:
                ranklist = [rank]
            else:
                ranklist = []
        else:
            start = int(self.request.get('start', '0'))
            ranklist = Rank.all().order('-__key__').fetch(20, start)
        pre = start - 20
        if pre < 0:
            pre = 0
        nex = start + 20
        self.render('template/rank/rankList.html',
                    {'ranklist': ranklist, 'pre': pre, 'nex': nex, 'limit': 20, 'count': len(ranklist),
                     'pluginurl': WEBURL, 'appcode': appcode})

    def post(self):
        return self.get()

class RankPluginList(Page):
    def get(self):
        cachename = 'ranklist'
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        l = []
        for r in Rank.all().order('-__key__'):
            l.append(r.id)
        self.getResult(True, u'', ','.join(l), cachename=cachename)


class RankCreate(Page):
    def get(self):
        appcode = self.request.get('appcode', '')
        cachename = 'ranklist_%s' % appcode
        cacheresult = memcache.get(cachename)
        if cacheresult:
            self.flush(cacheresult)
            return
        if appcode:
            rank = Rank.get_by_key_name(appcode)
            rlist = []
            if rank:
                for i in range(len(rank.points)):
                    rlist.append({'point': rank.points[i], 'rank': rank.ranks[i]})
        else:
            rlist = []
        self.getResult(True, u'保存积分设置成功', {"appcode": appcode, 'rlist': rlist},cachename=cachename)
        # self.render('template/rank/rankUpdate.html',
        #             {'rank': rank, 'rlist': rlist, 'elist': elist, 'pluginurl': WEBURL, 'appcode': appcode})

    def post(self):
        appcode = self.request.get('appcode', None)
        id = self.request.get('id', None)
        cachename = 'ranklist_%s' % appcode
        memcache.delete(cachename)
        num = self.request.get('num', '40')
        if appcode:
            rank = Rank.get_by_key_name(appcode)
            if not rank:
                rank = Rank(key_name=appcode)
                rank.id = id
                memcache.delete( 'ranklist')
            rank.points = []
            rank.ranks = []
            for i in range(int(num)):
                point = self.request.get('point%s' % i, None)
                rankstr = self.request.get('rank%s' % i, None)
                if point and rankstr:
                    rank.points.append(int(point))
                    rank.ranks.append(rankstr)
            rank.put()

            self.getResult(True, u'保存积分设置成功', None)
            # self.render('template/rank/rankUpdate.html', {'rank': rank, 'rlist': rlist, 'elist': elist, 'pluginurl': WEBURL, 'appcode':appcode, 'result':'succeed', 'msg':u'保存成功'})
        else:
            self.getResult(False, u'应用包名不存在', None)
            # self.render('template/rank/rankUpdate.html', {'rank': None, 'rlist': rlist, 'elist': elist, 'pluginurl': WEBURL, 'appcode':appcode, 'result':'warning', 'msg':u'应用包名不存在'})


class RankDelete(Page):
    def get(self):
        appcode = self.request.get('appcode', None)
        if appcode:
            rank = Rank.get_by_key_name(appcode)
            rank.delete()
        self.flush(getResult(appcode, True, u'删除成功'))