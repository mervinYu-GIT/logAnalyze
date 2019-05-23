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


    

#---------------------------------------- Test ----------------------------------------#
class TestNavLog(unittest.TestCase):
    """ test class navLog """
    def setUp(self):
        test_file = "loganalysis/navigation-logs/navigation10.log"
        self.test_nav_log = NavLogFile(test_file)
        self.test_case_1 = "P12.R080.02 :Start marker for navigation route calculation"
        self.test_case_2 = "P12.R080.02,P12.R081.02 :End marker for navigation route calculation"
        self.test_result_1 = ["1.01.2000 12:04:07:396", "1.01.2000 12:04:07:638", "1.01.2000 12:04:29:286",
                    "1.01.2000 12:04:42:168", "1.01.2000 12:05:29:957", "1.01.2000 12:06:05:757",
                    "1.01.2000 12:07:42:771", "1.01.2000 12:08:12:428", "1.01.2000 12:08:29:815",
                    "1.01.2000 12:09:05:321", "1.01.2000 12:09:42:898", "1.01.2000 12:10:37:201",
                    "1.01.2000 12:11:17:357", "1.01.2000 12:11:46:162", "1.01.2000 12:13:11:671",
                    "1.01.2000 12:15:10:786", "1.01.2000 12:25:05:919", "1.01.2000 12:25:17:362",
                    "1.01.2000 12:25:17:916", "1.01.2000 12:26:20:843", "1.01.2000 12:26:33:944",
                    "1.01.2000 12:28:46:275", "1.01.2000 12:29:02:231", "1.01.2000 12:30:17:221",
                    "1.01.2000 12:30:39:238", "1.01.2000 12:31:29:217", "1.01.2000 12:31:48:495",
                    "1.01.2000 12:32:00:831", "1.01.2000 12:35:07:693", "1.01.2000 12:40:01:892",
                    "1.01.2000 12:44:08:520"]
        self.test_result_2 = ["1.01.2000 12:04:10:556", "1.01.2000 12:04:31:272", "1.01.2000 12:04:43:975",
                  "1.01.2000 12:05:31:834", "1.01.2000 12:06:07:557", "1.01.2000 12:07:45:031",
                  "1.01.2000 12:08:14:355","1.01.2000 12:08:32:588","1.01.2000 12:09:07:160",
                  "1.01.2000 12:09:44:983","1.01.2000 12:10:52:662","1.01.2000 12:11:29:062",
                  "1.01.2000 12:11:58:786","1.01.2000 12:13:29:231","1.01.2000 12:15:27:338",
                  "1.01.2000 12:25:07:829","1.01.2000 12:25:18:620","1.01.2000 12:26:27:366",
                  "1.01.2000 12:26:41:088", "1.01.2000 12:28:54:558", "1.01.2000 12:29:07:479",
                  "1.01.2000 12:35:12:277", "1.01.2000 12:40:05:734", "1.01.2000 12:44:13:311"]
        self.test_times1 = [1,3,6,9,12,14]
        self.test_times2 = [4,7,8,10,11,15]
        self.test_result = [3,4,6,7,9,10,14,15]


    def test_searchLogs(self):
        key = self.test_case_1
        item = 'Message'
        result = self.test_result_1
        times = []

        logs = self.test_nav_log.searchLogs(key, item)
        for log in logs:
            times.append(log[1])

        self.assertListEqual(times, result)


    def test_getLogsTime(self):
        results = []
        key = self.test_case_2
        logs = self.test_nav_log.searchLogs(key, "Message")
        times = self.test_nav_log.getLogsTime(logs)
        for mg in self.test_result_2:
            mg_time = datetime.strptime(mg, "%d.%m.%Y %H:%M:%S:%f")
            results.append(mg_time)

        self.assertListEqual(times, results)


    # def test_logTimeMatching(self):
    #     test_times1 = [1,3,6,9,12,14]
    #     test_times2 = [4,7,8,10,11,15]
    #     test_result = [3,4,6,7,9,10,14,15]

    #     result = self.test_nav_log.logTimeMatching(test_times1, test_times2)

    #     self.assertListEqual(test_result, result)

    
    def test_getDeltaTime(self):
        begin_times = self.test_times1
        end_times = self.test_times2
        dest_results = [1,1,1,1]

        results = self.test_nav_log.getDeltaTime(begin_times, end_times)

        self.assertLessEqual(dest_results, results)



# unittest.main()