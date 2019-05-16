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
                        elif curLine.find('|') != -1:
                            while True:
                                index += 1
                                nextLine = file_lines[index]
                                if nextLine.find('|') != -1:
                                    if index == list_len - 1:   # last list item
                                        self.__listAppend(curLine)
                                        self.__listAppend(nextLine)
                                        break
                                    else:
                                        self.__listAppend(curLine)
                                        curLine = nextLine
                                        continue
                                elif nextLine.isspace():
                                    self.__listAppend(curLine)
                                    break
                                else:
                                    curLine += nextLine
                                    continue
        except IOError:
            print(self.inputFile + " open faild!")
            sys.exit()

        self.begin_time = datetime.strptime(self.logList[0][1], "%d.%m.%Y %H:%M:%S:%f")
        self.end_time = datetime.strptime(self.logList[-1][1], "%d.%m.%Y %H:%M:%S:%f")

        # write self.logList to debug file
        # with open('./debug_file.txt', 'w') as file_db:
        #     for log in self.logList:
        #         file_db.write(str(log) + '\n')

        
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


    def __listAppend(self, log):
        self.logList.append(log.split('|'))


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
            try:
                if key in log[self.logHeadRow.index(item)]:
                    return datetime.strptime(log[self.logHeadRow.index('Time')], \
                        "%d.%m.%Y %H:%M:%S:%f")
            except IndexError:
                print('key = ' + key)
                print('-------------------------------------------------------------------------------')
                print(log)
                sys.exit()
        return -1


    