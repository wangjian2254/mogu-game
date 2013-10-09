#coding=utf-8
#author:u'王健'
#Date: 13-6-1
#Time: 下午9:21

__author__ = u'王健'

from google.appengine.ext import db


class Points(db.Model):
    '''
    key_name : gamecode + _ + username
    '''
    point = db.IntegerProperty()#游戏积分

