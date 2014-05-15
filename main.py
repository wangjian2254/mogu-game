#coding=utf-8
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from gameserver.gamespace import CreateSpace, AddSpace, GetHotSpace, GetSpace, UploadPoint, GetAllPoint, QuiteSpace
from mogu.point import PointUpdate, PointQuery, UserPointQuery
from mogu.rank import RankList, RankCreate, RankDelete
from mogu.room import RoomList, RoomCreate, RoomDelete


app = webapp2.WSGIApplication([


                                ('/PointUpdate', PointUpdate),#积分上传
                                ('/PointQuery', PointQuery),#积分查询
                                ('/UserPointQuery', UserPointQuery),#用户个人所有游戏积分查询


                                ('/RankList',RankList),# 已有积分名称的游戏列表
                                ('/RankCreate',RankCreate),# 创建游戏的积分等级
                                ('/RankDelete',RankDelete),# 删除游戏的积分等级

                                ('/RoomList',RoomList),# 已有积分名称的游戏列表
                                ('/RoomCreate',RoomCreate),# 创建游戏的积分等级
                                ('/RoomDelete',RoomDelete),# 创建游戏的积分等级

                                ('/CreateSpace', CreateSpace),
                                ('/AddSpace', AddSpace),
                                ('/QuiteSpace', QuiteSpace),
                                ('/GetHotSpace', GetHotSpace),
                                ('/GetSpace', GetSpace),
                                ('/UploadPoint', UploadPoint),
                                ('/GetAllPoint', GetAllPoint),




], debug=True)
