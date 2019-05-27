#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from itertools import izip
import unittest

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return izip(a, a)

class NavLogFile:
    """ NavLogFile have entire message belong to navigation log file,
        and we can get some useful message in it. """

    def __init__(self, navLogFile):
        self.inputFile = navLogFile
        self.logHeadRow = []          # log head
        self.logList = []             # log message list
        self.begin_time = None
        self.end_time = None

        if self.inputFile[-4:] != '.log':
            print("valid file!")
            sys.exit()

        try:
            with open(self.inputFile, 'r') as fd:
                file_lines = fd.readlines()
                if not file_lines:
                    print('log file is empty!')
                    sys.exit()
                else:
                    self.logHeadRow = file_lines[0][:-1].split('|')
                    index = 0
                    list_len = len(file_lines)
                    while index < list_len - 1:        # touch the list end
                        index += 1
                        curLine = file_lines[index]    
                        if index == list_len - 1:      # last list item, so we should break loop
                            self.__listAppend(curLine)
                            break
                        if curLine.isspace():          # list item is space, just ignore it
                            continue
                        elif curLine.find('|') == 3:
                            while True:
                                index += 1
                                nextLine = file_lines[index]
                                if nextLine.isspace():
                                    self.__listAppend(curLine)
                                    break
                                elif nextLine.find('|') == 3:
                                    if index == list_len - 1:   # last list item
                                        self.__listAppend(curLine)
                                        self.__listAppend(nextLine)
                                        break
                                    else:
                                        self.__listAppend(curLine)
                                        curLine = nextLine
                                        continue
                                else:
                                    curLine += nextLine
                                    continue
        except IOError:
            print(self.inputFile + " open faild!")
            sys.exit()

        self.begin_time = datetime.strptime(self.logList[0][1], "%d.%m.%Y %H:%M:%S:%f")
        self.end_time = datetime.strptime(self.logList[-1][1], "%d.%m.%Y %H:%M:%S:%f")

        
    # def itemParsing(self, item):
    #     """ search logs that have same log item and sort it """
    #     logItemDict = {}
    #     itemDict = {
    #         'count' : 0,
    #         'list' : []
    #     }
    #     try:
    #         itemIndex = self.logHeadRow.index(item)
    #     except:
    #         print('item invalid')
    #         sys.exit()
    #     else:
    #         for log in self.logList:
    #             if log[itemIndex] in logItemDict.keys():
    #                 logItemDict[item]['list'].append(log)
    #                 logItemDict[item]['count'] += 1
    #             else:
    #                 itemDict['count'] = 1
    #                 itemDict['list'].append(log)
    #                 logItemDict[item] = itemDict

    #     return logItemDict


    def __listAppend(self, log):
        self.logList.append(log.split('|'))


    def __logTimeMatching(self, times1, times2):
        t1_index = 0
        t2_index = 0
        time1 = 0
        time2 = 0
        times = []

        if not times1 or not times2:
            return times

        while t1_index < len(times1) and t2_index < len(times2):
            time1 = times1[t1_index]
            time2 = times2[t2_index]

            if time1 >= time2:
                t2_index += 1
                continue
            else:
                if t1_index != len(times1) - 1:
                    next_time1 = times1[t1_index + 1]
                else:
                    times.append(time1)
                    times.append(time2)
                    break
                if next_time1 < time2:
                    t1_index += 1
                    continue
                else:
                    times.append(time1)
                    times.append(time2)
                    t1_index += 1
                    t2_index += 1

        return times


    def beginTime(self):
        return self.begin_time


    def endTime(self):
        return self.end_time


    def getLogItem(self, log, item):
        return log[self.logHeadRow.index(item)]


    def searchLogs(self, key, item, start=0, end=-1):
        """ search log that we need. """
        logs = []
        for log in self.logList[start:end]:
            if key in log[self.logHeadRow.index(item)]:
                logs.append(log)
        return logs

    
    def getLogsTime(self, logs):
        times = []
        for log in logs:
            time = datetime.strptime(self.getLogItem(log, 'Time'), "%d.%m.%Y %H:%M:%S:%f")
            times.append(time)
        return times


    def getDeltaTime(self, begin_times, end_times):
        delta_times = []
        
        times = self.__logTimeMatching(begin_times, end_times)
        if times:
            for t1, t2 in pairwise(times):
                delta_times.append(t2-t1)
        
        return delta_times



    def searchTimes(self, key, item, start=0, end=-1):
        """ search log time that we need. """
        times = []
        for log in self.logList[start:end]:
            if key in log[self.logHeadRow.index(item)]:
                times.append(datetime.strptime(log[self.logHeadRow.index('Time')], \
                    "%d.%m.%Y %H:%M:%S:%f"))
        return times
