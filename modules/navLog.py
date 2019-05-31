#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from os import path
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


    def resultMatching(self, results1, results2):
        result1_index = 0
        result2_index = 0
        log1 = 0
        log2 = 0
        results = []

        if not results1 or not results2:
            return results

        while result1_index < len(results1) and result2_index < len(results2):
            log1 = results1[result1_index]["log"]
            log2 = results2[result2_index]["log"]
            time1 = self.getLogTime(log1)
            time2 = self.getLogTime(log2)

            if time1 >= time2:
                result2_index += 1
                continue
            else:
                if result1_index != len(results1) - 1:
                    next_log1 = results1[result1_index + 1]["log"]
                    next_time1 = self.getLogTime(next_log1)
                else:
                    results.append(log1)
                    results.append(log2)
                    break
                if next_time1 < time2:
                    result2_index += 1
                    continue
                else:
                    results.append(log1)
                    results.append(log2)
                    result1_index += 1
                    result2_index += 1

        return results


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
        logList = self.logList[:]
        results = []
        for log in self.logList[start:end]:
            if key in log[self.logHeadRow.index(item)]:
                result = {"index":0,"log":None}
                result["index"] = logList.index(log)
                result["log"] = log
                results.append(result)
        return results


    def searchLog(self, key, item, start=0, end=-1):
        for log in self.logList[start:end]:
            if key in log[self.logHeadRow.index(item)]:
                return log


    
    def getLogsTime(self, search_results):
        times = []
        for result in search_results:
            time = datetime.strptime(self.getLogItem(result['log'], 'Time'), "%d.%m.%Y %H:%M:%S:%f")
            times.append(time)
        return times


    def getLogTime(self, log):
        time = datetime.strptime(self.getLogItem(log, 'Time'), "%d.%m.%Y %H:%M:%S:%f")
        return time


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




class NavLog:
    def __init__(self):
        self.attribute = {"name":None, "begin_time":None, "end_time":None, "len":None, "items":[]}
        self.load_file = ""
        self.logs = []
        # self.nav_logs = []    #[{"attribute":self.attribute, "file":self.load_file}, ...]


    def loadLogFile(self, log_file, name=None):
        if log_file[-4:] != '.log':
            print("valid file!")
            sys.exit()
        else:
            self.load_file = log_file

        with open(log_file, 'r') as fd:
            file_lines = fd.readlines()
            if not file_lines:
                print('log file is empty!')
                sys.exit()
            else:
                # logHeadRow = file_lines[0][:-1].split('|')
                # self.attribute["items"] = logHeadRow
                index = 0
                list_len = len(file_lines)
                while index < list_len - 1:        # touch the list end
                    index += 1
                    curLine = file_lines[index]    
                    if index == list_len - 1:      # last list item, so we should break loop
                        # self.__listAppend(curLine)
                        self.logs.append(curLine)
                        break
                    if curLine.isspace():          # list item is space, just ignore it
                        continue
                    elif curLine.find('|') == 3:
                        while True:
                            index += 1
                            nextLine = file_lines[index]
                            if nextLine.isspace():
                                # self.__listAppend(curLine)
                                self.logs.append(curLine)
                                break
                            elif nextLine.find('|') == 3:
                                if index == list_len - 1:   # last list item
                                    # self.__listAppend(curLine)
                                    # self.__listAppend(nextLine)
                                    self.logs.append(curLine)
                                    self.logs.append(curLine)
                                    break
                                else:
                                    # self.__listAppend(curLine)
                                    self.logs.append(curLine)
                                    curLine = nextLine
                                    continue
                            else:
                                curLine += nextLine
                                continue
        if name:
            log_name = name
        else:
            log_name = path.basename(log_file).split('.')[0]
        self.attribute["name"] = log_name
        self.attribute["len"] = len(self.logs)
        self.attribute["begin_time"] = datetime.strptime(self.logs[0].split("|")[1], "%d.%m.%Y %H:%M:%S:%f")
        self.attribute["end_time"] = datetime.strptime(self.logs[-1].split("|")[1], "%d.%m.%Y %H:%M:%S:%f")

    
    def getBeginTime(self):
        time = self.attribute["begin_time"]
        return time


    def getEndTime(self):
        time = self.attribute["end_time"]
        return time


    def getLog(self, key, start=0, end=-1):
        """ return log """
        logs = self.logs[start:end]
        result = {}
        for log in logs:
            if key in log:
                log_split = log.split("|")
                result["message"] = log_split[-1]
                result["index"] = logs.index(log) + start
                result["time"] = datetime.strptime(log_split[1], "%d.%m.%Y %H:%M:%S:%f")
                break

        return result

 
    def getLogs(self, key):
        """ return log and log index """
        logs = self.logs[:]
        results = []

        for log in logs:
            if key in log:
                result = {"message":"", "index":0, "time":None}
                log_split = log.split("|")
                result["message"] = log_split[-1]
                result["index"] = logs.index(log)
                result["time"] = datetime.strptime(log_split[1], "%d.%m.%Y %H:%M:%S:%f")
                results.append(result)

        return results


        



                
        






    