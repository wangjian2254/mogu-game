#coding=utf-8
#author:u'王健'
#Date: 14-5-5
#Time: 下午9:00
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
                     'pluginurl': WEBURL, 'appcode':appcode})

    def post(self):
        return self.get()


class RankCreate(Page):
    def get(self):
        appcode = self.request.get('appcode', '')
        num = 0
        if appcode:
            rank = Rank.get_by_key_name(appcode)
            rlist = []
            if rank:
                for i in range(len(rank.points)):
                    rlist.append((num, rank.points[i], rank.ranks[i]))
                    num += 1
        else:
            rank = None
            rlist = []
        elist = []
        for i in range(20):
            elist.append((num, '', ''))
            num += 1
        self.render('template/rank/rankUpdate.html', {'rank': rank, 'rlist': rlist, 'elist': elist, 'pluginurl': WEBURL, 'appcode':appcode})

    def post(self):
        appcode = self.request.get('appcode', None)
        num = 0
        rlist = []
        elist = []
        if appcode:
            rank = Rank.get_by_key_name(appcode)
            if not rank:
                rank = Rank(key_name=appcode)
            rank.points = []
            rank.ranks = []
            for i in range(40):
                point = self.request.get('point%s' % i, None)
                rankstr = self.request.get('rank%s' % i, None)
                if point and rankstr:
                    rank.points.append(int(point))
                    rank.ranks.append(rankstr)
                    rank.put()
            if rank:
                for i in range(len(rank.points)):
                    rlist.append((num, rank.points[i], rank.ranks[i]))
                    num += 1
            for i in range(20):
                elist.append((num, '', ''))
                num += 1
            self.render('template/rank/rankUpdate.html', {'rank': rank, 'rlist': rlist, 'elist': elist, 'pluginurl': WEBURL, 'appcode':appcode, 'result':'succeed', 'msg':u'保存成功'})
        else:

            for i in range(20):
                elist.append((num, '', ''))
                num += 1
            self.render('template/rank/rankUpdate.html', {'rank': None, 'rlist': rlist, 'elist': elist, 'pluginurl': WEBURL, 'appcode':appcode, 'result':'warning', 'msg':u'应用包名不存在'})


class RankDelete(Page):
    def get(self):
        appcode = self.request.get('appcode', None)
        if appcode:
            rank = Rank.get_by_key_name(appcode)
            rank.delete()
        self.flush(getResult(appcode, True, u'删除成功'))