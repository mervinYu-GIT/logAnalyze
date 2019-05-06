#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

def calcTime(beginTime, endTime):
    """ 计算beginTime与endTime之间的时间间隔，以deltatime的格式返回 """
    try:
        delta_time = endTime - beginTime
        return delta_time
    except:
        print('endTime must bigger than beginTime.')
