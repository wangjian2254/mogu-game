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
from mogu.point import PointUpdate, PointQuery, UserPointQuery


app = webapp2.WSGIApplication([


    ('/PointUpdate', PointUpdate),#积分上传
    ('/PointQuery', PointQuery),#积分查询
    ('/UserPointQuery', UserPointQuery),#用户个人所有游戏积分查询



], debug=True)
