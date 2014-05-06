#coding=utf-8
#author:u'王健'
#Date: 14-5-5
#Time: 下午9:00
from mogu.models import Rank
from tools.page import Page

__author__ = u'王健'


class RankList(Page):
    def get(self):
        start = 0
        gamecode = self.request.get('gamecode', None)
        if gamecode:
            rank = Rank.get_by_key_name(gamecode)
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
        self.render('template/rank/rankList.html', {'ranklist': ranklist, 'pre': pre, 'nex': nex, 'limit': 20})

    def post(self):
        return self.get()


class RankCreate(Page):
    def get(self):
        gamecode = self.request.get('gamecode', None)
        if gamecode:
            rank = Rank.get_by_key_name(gamecode)
        else:
            rank = None
        self.render('template/rank/rankUpdate.html', {'rank': rank})

    def post(self):
        gamecode = self.request.get('gamecode',None)
        if gamecode:
            rank = Rank.get_by_key_name(gamecode)
            if not rank:
                rank = Rank(key_name=gamecode)
            rank.points = []
            rank.ranks = []
            for i in range(40):
                point = self.request.get('point%s'%i, None)
                rankstr = self.request.get('rank%s'%i, None)
                rank.points.append(point)
                rank.ranks.appand(rankstr)
                rank.put()
            self.redirect('/RankCreate?gamecode=%s'%gamecode)
        else:
            self.redirect('/RankCreate')