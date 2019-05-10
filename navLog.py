#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime


class NavLogFile:
    """ NavLogFile have entire message belong to navigation log file,
        and we can get some useful message in it. """

    def __init__(self, navLogFile):
        self.inputFile = navLogFile
        self.logHeadRow = []          # log head
        self.logList = []             # log message list

        if self.inputFile[-4:] != '.log':
            print("valid file!")
            sys.exit()

        try:
            with open(self.inputFile, 'r') as fd:
                self.logHeadRow = fd.readline()[:-1].split('|')       #first line is log head line
                # continue read until catch the end
                while   True:
                    curLine = fd.readline()
                    # print(type(curLine))   # debug unicode error.
                    if  curLine == '':     # catch end! so we should break.
                        break
                    elif    curLine.isspace(): # white space! drop it and continue
                        continue
                    # if we have this key words below, do some special
                    elif    curLine.find('halsystemsettingsadapter') != -1\
                            or curLine.find('Sending:  origin') != -1\
                            or curLine.find('Route request') != -1:
                            while True:
                                nextLine = fd.readline()
                                if nextLine.isspace():
                                    break
                                curLine = curLine + nextLine
                    self.logList.append(curLine.split('|'))
        except IOError:
            print(self.inputFile + " open faild!")
            sys.exit()
        self.begin_time = datetime.strptime(self.logList[0][1], "%d.%m.%Y %H:%M:%S:%f")
        self.end_time = datetime.strptime(self.logList[-1][1], "%d.%m.%Y %H:%M:%S:%f")

        
    def itemParsing(self, item):
        """ search logs that have same log item and sort it """
        logItemDict = {}
        itemDict = {
            'count' : 0,
            'list' : []
        }
        try:
            itemIndex = self.logHeadRow.index(item)
        except:
            print('item invalid')
            sys.exit()
        else:
            for log in self.logList:
                if log[itemIndex] in logItemDict.keys():
                    logItemDict[item]['list'].append(log)
                    logItemDict[item]['count'] += 1
                else:
                    itemDict['count'] = 1
                    itemDict['list'].append(log)
                    logItemDict[item] = itemDict

        return logItemDict


    def beginTime(self):
        return self.begin_time


    def endTime(self):
        return self.end_time


    def searchLog(self, key, item, start=0, end=-1):
        """ search log that we need. """
        logs = []
        for log in self.logList[start:end]:
            if key in log[self.logHeadRow.index(item)]:
                logs.append(log)
        return logs


    def searchLogs(self, item, point_start, point_end):
        """ search all routine log """
        logs = []
        index = 0
        for log in self.logList:
            if point_start in log[self.logHeadRow.index(item)]:
                logs.append(log)
            
            if point_end in log[self.logHeadRow.index(item)]:
                logs.append(log)

        while True:
            if index > len(logs) - 2:
                break
            if logs[index][self.logHeadRow.index(item)] \
                == logs[index+1][self.logHeadRow.index(item)]:
                del logs[index]
            index += 1
        return logs


    def searchTime(self, key, item, start=0, end=-1):
        """ search log time that we need. """
        for log in self.logList[start:end]:
            if key in log[self.logHeadRow.index(item)]:
                return datetime.strptime(log[self.logHeadRow.index('Time')], \
                    "%d.%m.%Y %H:%M:%S:%f")
        return -1


    