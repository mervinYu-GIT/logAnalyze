#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

def calcTime(beginTime, endTime):
    """ calc deltatime """
    try:
        delta_time = endTime - beginTime
        return delta_time
    except:
        print('endTime must bigger than beginTime.')
