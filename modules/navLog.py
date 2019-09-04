#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from os import path
from datetime import datetime
import unittest
import re



class NavLog:
    def __init__(self):
        self.attribute = {"name":None, "begin_time":None, "end_time":None, "len":None, "items":[]}
        self.load_file = ""
        self.logs = []
        # self.nav_logs = []    #[{"attribute":self.attribute, "file":self.load_file}, ...]


    def loadLogFile(self, log_file, name=None):
        logs = []
        pattern = r"\b(Dbg|Wrn|Inf|Crt|Ftl)\|"
        prog = re.compile(pattern)
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
                        logs.append(curLine)
                        break
                    if curLine.isspace():          # list item is space, just ignore it
                        continue
                    elif prog.search(curLine, 0, 5):
                        while True:
                            index += 1
                            nextLine = file_lines[index]
                            if nextLine.isspace():
                                # self.__listAppend(curLine)
                                logs.append(curLine)
                                break
                            elif prog.search(curLine, 0, 5):
                                if index == list_len - 1:   # last list item
                                    # self.__listAppend(curLine)
                                    # self.__listAppend(nextLine)
                                    logs.append(curLine)
                                    logs.append(curLine)
                                    break
                                else:
                                    # self.__listAppend(curLine)
                                    logs.append(curLine)
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
        self.attribute["len"] = len(logs)
        self.attribute["begin_time"] = datetime.strptime(logs[0].split("|")[1], "%d.%m.%Y %H:%M:%S:%f")
        self.attribute["end_time"] = datetime.strptime(logs[-1].split("|")[1], "%d.%m.%Y %H:%M:%S:%f")
        self.logs = logs[:]


    def selfLog(self, log_index):
        return self.logs[log_index]


    def selfLogs(self, start=0, end=-1):
        if start == end:
            return self.logs[start]
        else:
            return self.logs[start:end]


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














