#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime
import unittest


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


    def beginTime(self):
        return self.begin_time


    def endTime(self):
        return self.end_time


    def getLogItem(self, log, item):
        return log[self.logHeadRow.index(item)]


    def searchLog(self, key, item, start=0, end=-1):
        """ search log that we need. """
        logs = []
        for log in self.logList[start:end]:
            try:
                if key in log[self.logHeadRow.index(item)]:
                    logs.append(log)
            except IndexError:
                print (self.logHeadRow.index(item))
                print (log)
        return logs

    
    def getLogsTime(self, logs):
        times = []
        for log in logs:
            time = datetime.strptime(self.getLogItem(log, 'Time'), "%d.%m.%Y %H:%M:%S:%f")
            times.append(time)
        return times


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

    
    def getDeltaTime(self, begin_times, end_times):
        delta_times = []
        bt_index = 0     # begin times index
        et_index = 0     # end times index
        while bt_index < len(begin_times) or et_index < len(end_times):
            bt_cur = begin_times[bt_index]
            et_cur = end_times[et_index]

            if bt_cur < et_cur:
                # bounds checking
                if bt_index == len(begin_times) - 1 \
                    or et_index == len(end_times) - 1:
                    delta_time = et_cur - bt_cur
                    delta_times.append(delta_time)
                    break

                bt_next = begin_times[bt_index + 1]
                if bt_next < et_cur:
                    bt_index += 1
                    continue
                else:
                    delta_time = et_cur - bt_cur
                    bt_index += 1
                    et_index += 1
                    delta_times.append(delta_time)
            else:
                et_index += 1
        # print(delta_times)
        return delta_times


    def searchTime(self, key, item, start=0, end=-1):
        """ search log time that we need. """
        for log in self.logList[start:end]:
            if key in log[self.logHeadRow.index(item)]:
                return datetime.strptime(log[self.logHeadRow.index('Time')], \
                    "%d.%m.%Y %H:%M:%S:%f")
        return -1


    

#---------------------------------------- Test ----------------------------------------
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


    def test_getLogsTime(self):
        results = []
        key = self.test_case_2
        logs = self.test_nav_log.searchLog(key, "Message")
        times = self.test_nav_log.getLogsTime(logs)
        for mg in self.test_result_2:
            mg_time = datetime.strptime(mg, "%d.%m.%Y %H:%M:%S:%f")
            results.append(mg_time)

        self.assertListEqual(times, results)



    def test_getDeltaTime(self):
        """ test navLog::getDeltaTime """
        begin = self.test_cast_1
        end = self.test_cast_2
       

        dest_result = [ datetime.strptime("1.01.2000 12:04:10:556", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:04:07:638", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:04:31:272", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:04:29:286", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:04:43:975", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:04:42:168", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:05:31:834", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:05:29:957", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:06:07:557", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:06:05:757", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:07:42:771", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:07:45:031", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:08:14:355", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:08:12:428", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:08:32:588", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:08:29:815", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:09:07:160", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:09:05:321", "%d.%m.%Y %H:%M:%S:%f") ,

                        datetime.strptime("1.01.2000 12:09:44:983", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:09:42:898", "%d.%m.%Y %H:%M:%S:%f"), 

                        datetime.strptime("1.01.2000 12:10:52:662", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:10:37:201", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:11:29:062", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:11:17:357", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:11:58:786", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:11:46:162", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:13:29:231", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:13:11:671", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:15:27:338", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:15:10:786", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:25:07:829", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:25:05:919", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:25:18:620", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:25:17:362", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:26:27:366", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:26:20:843", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:26:41:088", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:26:33:944", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:28:54:558", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:28:46:275", "%d.%m.%Y %H:%M:%S:%f"),
                       
                        datetime.strptime("1.01.2000 12:29:07:479", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:29:02:231", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:35:12:277", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:35:07:693", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:40:05:734", "%d.%m.%Y %H:%M:%S:%f") \
                            - datetime.strptime("1.01.2000 12:40:01:892", "%d.%m.%Y %H:%M:%S:%f"),

                        datetime.strptime("1.01.2000 12:44:13:311", "%d.%m.%Y %H:%M:%S:%f") \
                           - datetime.strptime("1.01.2000 12:44:08:520", "%d.%m.%Y %H:%M:%S:%f")
                       ]
        delta_times = self.test_nav_log.getDeltaTime(begin, end)

        for time in delta_times:
            self.assertIn(time, dest_result)

# unittest.main()