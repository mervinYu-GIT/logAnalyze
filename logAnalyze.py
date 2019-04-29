#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import json
from datetime import datetime
from argparse import ArgumentParser

import xlwt   # need installed : pip install xlwt

class NavLogAnalyze:
    pass


def calcTime(beginTime, endTime):
    """ 计算beginTime与endTime之间的时间间隔，以deltatime的格式返回 """
    begin = datetime.strptime(beginTime, "%d.%m.%Y %H:%M:%S:%f")
    end = datetime.strptime(endTime, "%d.%m.%Y %H:%M:%S:%f")
    try:
        delta_time = end - begin
        return delta_time
    except:
        print('endTime must bigger than beginTime.')


def outPut(fileName, path='./log_xls'):
    if not os.path.exists('path'):
        os.mkdir('./log_xls')

    work_book.save(path + fileName)


class NavLog:
    """ 将提供的log文件转换成python可识别的数据类型 """

    def __init__(self, navLogFile):
        self.inputFile = navLogFile
        self.logHeadRow = []          # 存储log文件的首行
        self.logList = []             # 存储log文件的其它行
        self.logDict = {}             # 根据某种规则以字典的形式组织期望获取的log信息

        if self.inputFile[-4:] != '.log':
            print("valid file!")
            sys.exit()

        # 打开文件
        try:
            fd = open(self.inputFile, 'r')
        except IOError:
            print(self.inputFile + " open faild!")
            sys.exit()

        self.logHeadRow = fd.readline()[:-1].split('|')       #读取head行保存在logHeadRow中

        # 循环读取文件流中剩余的行并进行解析
        while   True:
            curLine = fd.readline()          # 读取当前行
            # print(curLine)
            if  curLine == '':     # 若当前行为空字符，表示读到文件末尾，跳出循环
                # print('end file!!--------')
                break
            elif    curLine.isspace(): # 当前行为空白字符，则丢弃并读取下一行
                continue
            # 若当前行存在目的字符串，表示接下来连续的几行都为当前log的信息，直到出现单独的空白符。
            elif    curLine.find('halsystemsettingsadapter') != -1\
                    or curLine.find('Sending:  origin') != -1\
                    or curLine.find('Route request') != -1:
                    print('--------------------hello------------------------------')
                    while True:
                        nextLine = fd.readline()
                        if nextLine.isspace():
                            break
                        curLine = curLine + nextLine
            # print(curLine)
            print(curLine.split('|'))
            self.logList.append(curLine.split('|'))

        fd.close()  #文件读取结束，关闭文件。

        self.begin_time = datetime.strptime(self.logList[0][1], "%d.%m.%Y %H:%M:%S:%f")
        self.end_time = datetime.strptime(self.logList[-1][1], "%d.%m.%Y %H:%M:%S:%f")

        
    def itemParsing(self, item):
        """ 根据提供的item(Log Level,PID,Category,File,Function,Message),对log数据进行分类,
        以字典的形式返回分析结果 """
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


    def search(self, key, item, start=0, end=-1):
        """ 在logList[start:end]的log item项中查找key """
        for log in self.logList[start:end]:
            if key in log[self.logHeadRow.index(item)]:
                print('log index: ' + str(self.logList.index(log)))
                print('-----------------------------------------')
                print(log[self.logHeadRow.index(item)])
                return log
        return -1


if __name__ == "__main__":

    # logAnalyze = LogAnalyze()
    # logAnalyze.runWork()

    arg_parser = ArgumentParser()
    arg_parser.add_argument('inputFile', help = "input log file")
    arg_parser.add_argument('--cfg', help="config file, eg: path/config.json")
    args = arg_parser.parse_args()

    if args.inputFile:
      nav_log1 = NavLog(args.inputFile)
    if args.cfg:
        config_file = args.cfg
    print('------------------------------------------------------------')

    # 创建excel文件
    work_book = xlwt.Workbook('utf-8')  # 工作簿
    work_sheet = work_book.add_sheet('navLog')
    # work_sheet.write(1, 0, 'this is test')
   


    # print(args)
    row = 0
    col = 0
    with open(config_file, 'r') as json_f:
        json_cfg = json.load(json_f)
        print(json_cfg)
        for k, v in json_cfg.items():
            work_sheet.write(row, col, k)
            for k_1, v_1 in v.items():
                col += 1
                work_sheet.write(row, col, k_1)
                for k_2, v_2 in v_1.items():
                    col += 1
                    if k_2 == 'log point':
                        """
                            1. 查找log
                            2. 求出deltatime
                            3. 转换deltatime
                            4. 写入work_sheet
                        """
                        # search log
                        for log in nav_log1.logList:
                            if k_2['begin'] in \
                            log[nav_log1.logHeadRow.index('Message')]:
                                beginTime = \
                                datetime.strptime(\
                                    log[nav_log1.logHeadRow.index('Time')],\
                                    '%d.%m.%Y %H:%M:%S:%f')
                        # pass
                    else:
                        work_sheet.write(row, col, v_2)
                row += 1
                col -= (len(v_1) + 1)
            row += 1
            col -= (len(v) - 2)

    work_book.save('./navLog.xls')


    if args.inputFile:
        nav_log1 = NavLog(args.inputFile)
    print('------------------------------------------------------------')
    # print('log begin time: ')
    # print(nav_log1.beginTime())
    # delta_time = calcTime(nav_log1.beginTime(), nav_log1.endTime())
    # print(delta_time)
    print(nav_log1.logHeadRow)
    print('----------------------------------------------------------')
    print(nav_log1.logList)
    log_start = nav_log1.search("System settings notification", 'Message')
    if log_start != -1:
        beginTime = datetime.strptime(log_start[nav_log1.logHeadRow.index('Time')],\
        "%d.%m.%Y %H:%M:%S:%f")
    else:
        beginTime = nav_log1.begin_time
        print('start point not found! begin time was seted to log begin time.')

    log_end = nav_log1.search("Sending:  origin", 'Message')
    if log_end != -1:
        endTime = datetime.strptime(log_end[nav_log1.logHeadRow.index('Time')],\
            "%d.%m.%Y %H:%M:%S:%f")
    else:
        endTime = nav_log1.end_time
        print('end point not found! end time was seted to log end time.')

    delta_time = calcTime(beginTime, endTime)
    print(delta_time)
    print(str(delta_time)[:-7])

