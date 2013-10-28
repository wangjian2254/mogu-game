#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午9:21

__author__ = u'王健'

from google.appengine.ext import db


class Points(db.Model):
    '''
    key_name : gamecode + ! + username
    '''
    # 假设用户对没有玩的游戏，失去兴趣了。
    #username = db.StringProperty() #用户名

    point = db.IntegerProperty() #游戏积分

