#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from os import path
import json
import re  
from datetime import datetime
from argparse import ArgumentParser
import collections
from modules.navXlsx import NavXlsxFile
from modules.navLog import NavLogFile, NavLog, pairwise


def calcTime(beginTime, endTime):
    """ calc deltatime """
    try:
        delta_time = endTime - beginTime
        return delta_time
    except:
        print('endTime must bigger than beginTime.')


def getFileList( p ):
    """ get file name that in dictory. """
    p = str( p )
    if p=="":
        return [ ]
    p = p.replace( "/","\\")
    if p[ -1] != "\\":
        p = p+"\\"
    a = os.listdir( p )
    b = [ x   for x in a if os.path.isfile( p + x ) ]
    return b


# sort string containning numbers
re_digits = re.compile(r'(\d+)')  
def embedded_numbers(s):  
     pieces = re_digits.split(s)               # split num and asc  
     pieces[1::2] = map(int, pieces[1::2])     # exchange the num  
     return pieces  
def sort_strings_with_embedded_numbers(alist):  
     return sorted(alist, key=embedded_numbers , reverse = True)


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument('log_files', nargs = '*', help = "input log file")
    arg_parser.add_argument('--cfg', help="config file, eg: path/config.json")
    arg_parser.add_argument('--xlsx', help='xlsx file')
    args = arg_parser.parse_args()

    log_files = []
    if args.log_files:
        for f_p in args.log_files:
            if os.path.isdir(f_p):
                files = getFileList(f_p)
                for file in files:
                    if '.log' in file:
                        log_files.append(f_p + file)
            elif '.log' in f_p:
                log_files.append(f_p)
    if len(log_files) > 1:
        log_files = sort_strings_with_embedded_numbers(log_files)

    if args.cfg:
        cfg_file = args.cfg
    else:
        cfg_file = './config.json'

    if args.xlsx:
        xlsx_file_path = args.xlsx
    else:
        xlsx_file_path = './navLog.xlsx'

    xlsx_file = NavXlsxFile()
    nav_log = NavLog()
    with open(cfg_file, 'r') as json_file:
        try:
            json_data = json.load(json_file, object_pairs_hook=collections.OrderedDict)
        except:
            print(cfg_file + ' is not json format!')
            sys.exit()

        for log_file in log_files:
            # nav_log_file = NavLogFile(log_file)
            log_file_name = path.basename(log_file).split('.')[0]
            nav_log.loadLogFile(log_file, log_file_name)
            sheet_name = log_file_name
            xlsx_file.createSheet(sheet_name)
            work_sheet = xlsx_file.selectSheet(sheet_name)
            
            origin_point = {'row':1, 'col':1}
            route_cursor = {}
            search_cursor = {}
            route_flag = 0
            search_flag = 0

            # sheet_data attribute
            sheet_data_attr = {}

            for k, v in json_data.items():
                k = k.encode("utf-8")
                print("k = " + k)
                # print(type(k))
                if k == "boot-up":
                    print('in ' + k)
                    row_offset = 0
                    col_offset = 0 

                    xlsx_file.writeCell(origin_point['row'] ,origin_point['col'], k)
                    col_offset += 1
                    row_offset += 1
                    index = 1

                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")
                        print("k1 = " + k_1)
                        if k_1 == "loading libfordhal.so":
                            print("in " + k_1)
                            xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                origin_point['col'] + col_offset - 1, index)
                            index += 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    if work_sheet.cell(origin_point['row'], \
                                        origin_point['col'] + col_offset).value == None:

                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, "time cost")

                                    if begin:
                                        begin_log = nav_log.getLog(begin, "Message")
                                        if begin_log:
                                            time_str = begin_log["log"][nav_log.getItemIndex("Time")]
                                            begin_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_log = nav_log.getLog(end, "Message")
                                        if end_log:
                                            time_str = end_log["log"][nav_log.getItemIndex("Time")]
                                            end_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time
                                        xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                            origin_point['col'] + col_offset, delta_time.total_seconds())
                                        print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + k_2)

                            col_offset = 1
                            row_offset += 1
                           
                        elif k_1 == "loading FHC":
                            print("in " + k_1)
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset - 1, index)
                                    index += 1
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    if work_sheet.cell(origin_point['row'], \
                                        origin_point['col'] + col_offset).value == None:

                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, "time cost")

                                    if begin:
                                        begin_log = nav_log.getLog(begin, "Message")
                                        if begin_log:
                                            time_str = begin_log["log"][nav_log.getItemIndex("Time")]
                                            begin_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_log = nav_log.getLog(end, "Message")
                                        if end_log:
                                            time_str = end_log["log"][nav_log.getItemIndex("Time")]
                                            end_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time
                                        xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                            origin_point['col'] + col_offset, delta_time.total_seconds())
                                        print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + k_2)

                            col_offset = 1
                            row_offset += 1
                            pass
                        elif k_1 == "loading libqtarp.so":
                            print("in " + k_1)
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset - 1, index)
                                    index += 1
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    if work_sheet.cell(origin_point['row'], \
                                        origin_point['col'] + col_offset).value == None:

                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, "time cost")

                                    if begin:
                                        begin_log = nav_log.getLog(begin, "Message")
                                        if begin_log:
                                            time_str = begin_log["log"][nav_log.getItemIndex("Time")]
                                            begin_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_log = nav_log.getLog(end, "Message")
                                        if end_log:
                                            time_str = end_log["log"][nav_log.getItemIndex("Time")]
                                            end_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time
                                        xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                            origin_point['col'] + col_offset, delta_time.total_seconds())
                                        print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + k_2)

                            col_offset = 1
                            row_offset += 1
                            pass
                        elif k_1 == "FordHAL Init":
                            print("in " + k_1)
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset - 1, index)
                                    index += 1
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    if work_sheet.cell(origin_point['row'], \
                                        origin_point['col'] + col_offset).value == None:

                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, "time cost")

                                    if begin:
                                        begin_log = nav_log.getLog(begin, "Message")
                                        if begin_log:
                                            time_str = begin_log["log"][nav_log.getItemIndex("Time")]
                                            begin_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_log = nav_log.getLog(end, "Message")
                                        if end_log:
                                            time_str = end_log["log"][nav_log.getItemIndex("Time")]
                                            end_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time
                                        xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                            origin_point['col'] + col_offset, delta_time.total_seconds())
                                        print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + k_2)

                            col_offset = 1
                            row_offset += 1
                            pass
                        elif k_1 == "loading QML":
                            print("in " + k_1)
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset - 1, index)
                                    index += 1
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    if work_sheet.cell(origin_point['row'], \
                                        origin_point['col'] + col_offset).value == None:

                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, "time cost")

                                    if begin:
                                        begin_log = nav_log.getLog(begin, "Message")
                                        if begin_log:
                                            time_str = begin_log["log"][nav_log.getItemIndex("Time")]
                                            begin_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_log = nav_log.getLog(end, "Message")
                                        if end_log:
                                            time_str = end_log["log"][nav_log.getItemIndex("Time")]
                                            end_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time
                                        xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                            origin_point['col'] + col_offset, delta_time.total_seconds())
                                        print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + k_2)

                            col_offset = 1
                            row_offset += 1
                            pass
                        elif k_1 == "SDK Init":
                            print("in " + k_1)
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset - 1, index)
                                    index += 1
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    if work_sheet.cell(origin_point['row'], \
                                        origin_point['col'] + col_offset).value == None:

                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, "time cost")

                                    if begin:
                                        begin_log = nav_log.getLog(begin, "Message")
                                        if begin_log:
                                            time_str = begin_log["log"][nav_log.getItemIndex("Time")]
                                            begin_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_log = nav_log.getLog(end, "Message")
                                        if end_log:
                                            time_str = end_log["log"][nav_log.getItemIndex("Time")]
                                            end_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time
                                        xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                            origin_point['col'] + col_offset, delta_time.total_seconds())
                                        print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + k_2)

                            col_offset = 1
                            row_offset += 1
                            pass
                        elif k_1 == "Loading HMI":
                            print("in " + k_1)
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset - 1, index)
                                    index += 1
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    if work_sheet.cell(origin_point['row'], \
                                        origin_point['col'] + col_offset).value == None:

                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, "time cost")

                                    if begin:
                                        begin_log = nav_log.getLog(begin, "Message")
                                        if begin_log:
                                            time_str = begin_log["log"][nav_log.getItemIndex("Time")]
                                            begin_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_log = nav_log.getLog(end, "Message")
                                        if end_log:
                                            time_str = end_log["log"][nav_log.getItemIndex("Time")]
                                            end_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time
                                        xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                            origin_point['col'] + col_offset, delta_time.total_seconds())
                                        print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + k_2)

                            col_offset = 1
                            row_offset += 1
                            pass
                        elif k_1 == "total":
                            print("in " + k_1)
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset - 1, index)
                                    index += 1
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    if work_sheet.cell(origin_point['row'], \
                                        origin_point['col'] + col_offset).value == None:

                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, "time cost")

                                    if begin:
                                        begin_log = nav_log.getLog(begin, "Message")
                                        if begin_log:
                                            time_str = begin_log["log"][nav_log.getItemIndex("Time")]
                                            begin_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_log = nav_log.getLog(end, "Message")
                                        if end_log:
                                            time_str = end_log["log"][nav_log.getItemIndex("Time")]
                                            end_time = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S:%f")
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time
                                        xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                            origin_point['col'] + col_offset, delta_time.total_seconds())
                                        print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + k_2)

                            col_offset = 1
                            row_offset += 1
                            pass
                       
                elif k == "Routing":
                    print("in " + k)
                    origin_point["row"] = work_sheet.max_row + 3
                    print("Routing origin row: " + str(origin_point["row"]))
                    row_offset = 0
                    col_offset = 0 
                    routing_avg = {"max_col":0}

                    xlsx_file.writeCell(origin_point['row'] ,origin_point['col'], k)
                    col_offset += 1
                    row_offset += 1
                    index = 1
                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")
                        if k_1 == "Calculate Route":
                            print("in " + k_1)
                            xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                origin_point['col'] + col_offset - 1, index)
                            index += 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_logs = []
                                    end_logs = []
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    

                                    if begin:
                                        begin_logs = nav_log.getLogs(begin, "Message")
                                    else:
                                        pass
                                    
                                    if end:
                                        end_logs = nav_log.getLogs(end, "Message")
                                    else:
                                        pass

                                    if begin_logs and end_logs:
                                        index1 = 0
                                        index2 = 0
                                        match_logs = []
                                        while index1 < len(begin_logs) and index2 < len(end_logs):
                                            begin_index = begin_logs[index1]["index"]
                                            end_index = end_logs[index2]["index"]

                                            if begin_index >= end_index:
                                                index2 += 1
                                                continue
                                            else:
                                                if index1 != len(begin_logs) - 1:
                                                    next_begin_index = begin_logs[index1 + 1]["index"]
                                                else:
                                                    match_logs.append(begin_logs[index1])
                                                    match_logs.append(end_logs[index2])
                                                    break
                                                if next_begin_index < end_index:
                                                    index1 += 1
                                                    continue
                                                else:
                                                    match_logs.append(begin_logs[index1])
                                                    match_logs.append(end_logs[index2])
                                                    index1 += 1
                                                    index2 += 2
                                        groups = {}
                                        for begin, end in pairwise(match_logs):
                                            # member = {}
                                            member_name = None
                                            delta_time = None
                                            key = "Sending:  origin"
                                            result = nav_log.getLog(key, "Message", begin["index"], end["index"])
                                            if result:
                                                result_message = result["log"][nav_log.getItemIndex("Message")]
                                                addr_index = result_message.index("formatted_address:")
                                                member_name = result_message[result_message.index("\"", addr_index) + 1:\
                                                    result_message.index("\n", addr_index) - 1]
                                                # member["name"] = member_name

                                                begin_time_str = begin["log"][nav_log.getItemIndex("Time")]
                                                end_time_str = end["log"][nav_log.getItemIndex("Time")]
                                                begin_time = datetime.strptime(begin_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                                end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                                delta_time = end_time - begin_time
                                            else:
                                                key = "Route request:"
                                                result = nav_log.getLog(key, "Message", begin["index"], end["index"])
                                                if result:
                                                    result_message = result["log"][nav_log.getItemIndex("Message")]
                                                    addr_index = result_message.index("formatted_address:")
                                                    member_name = result_message[result_message.index("\"", addr_index) + 1:\
                                                        result_message.index("\n", addr_index) - 1]
                                                    # member["name"] = member_name

                                                    begin_time_str = begin["log"][nav_log.getItemIndex("Time")]
                                                    end_time_str = end["log"][nav_log.getItemIndex("Time")]
                                                    begin_time = datetime.strptime(begin_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                                    end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                                    delta_time = end_time - begin_time
                                                else:
                                                    continue

                                            if groups.has_key(member_name):
                                                groups[member_name].append(delta_time)
                                            else:
                                                groups[member_name] = []
                                                groups[member_name].append(delta_time)
                                    
                                        print(groups)
                                        if work_sheet.cell(origin_point['row'], \
                                        origin_point['col'] + col_offset).value == None:

                                            xlsx_file.writeCell(origin_point['row'], \
                                                origin_point['col'] + col_offset, "group for destination")

                                        avg_col = 0
                                        cal_route_avgs = []
                                        for group_name, members in groups.items():
                                            sub_col_offset = col_offset
                                            xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                                origin_point['col'] + sub_col_offset, group_name)
                                            # print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)
                                            sub_col_offset += 1

                                            delta_total = 0
                                            delta_cnt = 0
                                            for member in members:
                                                delta_cnt += 1
                                                delta_total += member.total_seconds()
                                                if work_sheet.cell(origin_point['row'], \
                                                    origin_point['col'] + sub_col_offset).value == None:

                                                    xlsx_file.writeCell(origin_point['row'], \
                                                        origin_point['col'] + sub_col_offset, "time cost Rand(" + str(delta_cnt) + ")")

                                                xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                                    origin_point['col'] + sub_col_offset, member.total_seconds())
                                                # print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + member.total_seconds())
                                                sub_col_offset += 1
                                            
                                            # get cal_route_avgs
                                            if delta_cnt > 1:
                                                cal_route_avgs.append(round(delta_total/delta_cnt, 3))
                                            else:
                                                cal_route_avgs.append(None)

                                            # get max col for avg
                                            if routing_avg["max_col"] < sub_col_offset:
                                                routing_avg["max_col"] = sub_col_offset

                                            row_offset += 1
                                        
                                        if work_sheet.cell(origin_point['row'], \
                                            origin_point['col'] + routing_avg["max_col"]).value == None:

                                            xlsx_file.writeCell(origin_point['row'], \
                                                origin_point['col'] + routing_avg["max_col"], "avg")

                                        print(cal_route_avgs)
                                        routing_avg["cal_route_avg"] = cal_route_avgs
                                        for avg in cal_route_avgs:
                                            if avg:
                                                xlsx_file.writeCell(origin_point['row'] + cal_route_avgs.index(avg) + 1, \
                                                    origin_point['col'] + routing_avg["max_col"], avg)

                            col_offset = 1
                            # row_offset += 1
                            pass
                        elif k_1 == "Calculate Guidance":
                            print("in " + k_1)
                            xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                origin_point['col'] + col_offset - 1, index)
                            index += 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "owner":
                                    if work_sheet.cell(origin_point['row'], \
                                    origin_point['col'] + col_offset).value == None:                   
                                        xlsx_file.writeCell(origin_point['row'], \
                                            origin_point['col'] + col_offset, k_2)

                                    xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        origin_point['col'] + col_offset, v_2)
                                    print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)

                                    col_offset += 1

                                elif k_2 == "log point":
                                    begin_logs = []
                                    end_logs = []
                                    begin = v_2["begin"]
                                    end = v_2["end"]
                                    

                                    if begin:
                                        begin_logs = nav_log.getLogs(begin, "Message")
                                    else:
                                        pass
                                    
                                    if end:
                                        end_logs = nav_log.getLogs(end, "Message")
                                    else:
                                        pass

                                    if begin_logs and end_logs:
                                        index1 = 0
                                        index2 = 0
                                        match_logs = []
                                        while index1 < len(begin_logs) and index2 < len(end_logs):
                                            begin_index = begin_logs[index1]["index"]
                                            end_index = end_logs[index2]["index"]

                                            if begin_index >= end_index:
                                                index2 += 1
                                                continue
                                            else:
                                                if index1 != len(begin_logs) - 1:
                                                    next_begin_index = begin_logs[index1 + 1]["index"]
                                                else:
                                                    match_logs.append(begin_logs[index1])
                                                    match_logs.append(end_logs[index2])
                                                    break
                                                if next_begin_index < end_index:
                                                    index1 += 1
                                                    continue
                                                else:
                                                    match_logs.append(begin_logs[index1])
                                                    match_logs.append(end_logs[index2])
                                                    index1 += 1
                                                    index2 += 2

                                        delta_times = []
                                        delta_cnt = 0
                                        for begin_log, end_log in pairwise(match_logs):
                                            delta_cnt += 1
                                            begin_time_str = begin_log["log"][nav_log.getItemIndex("Time")]
                                            end_time_str = end_log["log"][nav_log.getItemIndex("Time")]
                                            begin_time = datetime.strptime(begin_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                            end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                            delta_time = end_time - begin_time
                                            if work_sheet.cell(origin_point['row'], \
                                                origin_point['col'] + col_offset + delta_cnt).value == None:

                                                xlsx_file.writeCell(origin_point['row'], \
                                                    origin_point['col'] + col_offset + delta_cnt, "time cost Rand(" + str(delta_cnt) + ")")
                                            xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                                    origin_point['col'] + col_offset + delta_cnt, delta_time.total_seconds())

                                            delta_times.append(delta_time)
                                        

                                        # groups = {}
                                        # for begin, end in pairwise(match_logs):
                                        #     # member = {}
                                        #     member_name = None
                                        #     delta_time = None
                                        #     key = "Sending:  origin"
                                        #     result = nav_log.getLog(key, "Message", begin["index"], end["index"])
                                        #     if result:
                                        #         result_message = result["log"][nav_log.getItemIndex("Message")]
                                        #         addr_index = result_message.index("formatted_address:")
                                        #         member_name = result_message[result_message.index("\"", addr_index) + 1:\
                                        #             result_message.index("\n", addr_index) - 1]
                                        #         # member["name"] = member_name

                                        #         begin_time_str = begin["log"][nav_log.getItemIndex("Time")]
                                        #         end_time_str = end["log"][nav_log.getItemIndex("Time")]
                                        #         begin_time = datetime.strptime(begin_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                        #         end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                        #         delta_time = end_time - begin_time
                                        #     else:
                                        #         key = "Route request:"
                                        #         result = nav_log.getLog(key, "Message", begin["index"], end["index"])
                                        #         if result:
                                        #             result_message = result["log"][nav_log.getItemIndex("Message")]
                                        #             addr_index = result_message.index("formatted_address:")
                                        #             member_name = result_message[result_message.index("\"", addr_index) + 1:\
                                        #                 result_message.index("\n", addr_index) - 1]
                                        #             # member["name"] = member_name

                                        #             begin_time_str = begin["log"][nav_log.getItemIndex("Time")]
                                        #             end_time_str = end["log"][nav_log.getItemIndex("Time")]
                                        #             begin_time = datetime.strptime(begin_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                        #             end_time = datetime.strptime(end_time_str, "%d.%m.%Y %H:%M:%S:%f")
                                        #             delta_time = end_time - begin_time
                                        #         else:
                                        #             continue

                                        #     if groups.has_key(member_name):
                                        #         groups[member_name].append(delta_time)
                                        #     else:
                                        #         groups[member_name] = []
                                        #         groups[member_name].append(delta_time)
                                    
                                        # print(groups)
                                        # if work_sheet.cell(origin_point['row'], \
                                        # origin_point['col'] + col_offset).value == None:

                                        #     xlsx_file.writeCell(origin_point['row'], \
                                        #         origin_point['col'] + col_offset, "group for destination")

                                        # avg_col = 0
                                        # cal_route_avgs = []
                                        # for group_name, members in groups.items():
                                        #     sub_col_offset = col_offset
                                        #     xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        #         origin_point['col'] + sub_col_offset, group_name)
                                        #     # print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + v_2)
                                        #     sub_col_offset += 1

                                        #     delta_total = 0
                                        #     delta_cnt = 0
                                        #     for member in members:
                                        #         delta_cnt += 1
                                        #         delta_total += member.total_seconds()
                                        #         if work_sheet.cell(origin_point['row'], \
                                        #             origin_point['col'] + sub_col_offset).value == None:

                                        #             xlsx_file.writeCell(origin_point['row'], \
                                        #                 origin_point['col'] + sub_col_offset, "time cost Rand(" + str(delta_cnt) + ")")

                                        #         xlsx_file.writeCell(origin_point['row'] + row_offset, \
                                        #             origin_point['col'] + sub_col_offset, member.total_seconds())
                                        #         # print(str(origin_point['row'] + row_offset) + str(origin_point['col'] + col_offset) + member.total_seconds())
                                        #         sub_col_offset += 1
                                            
                                        #     # get cal_route_avgs
                                        #     if delta_cnt > 1:
                                        #         cal_route_avgs.append(round(delta_total/delta_cnt, 3))
                                        #     else:
                                        #         cal_route_avgs.append(None)

                                        #     # get max col for avg
                                        #     if routing_avg["max_col"] < sub_col_offset:
                                        #         routing_avg["max_col"] = sub_col_offset

                                        #     row_offset += 1
                                        
                                        # if work_sheet.cell(origin_point['row'], \
                                        #     origin_point['col'] + routing_avg["max_col"]).value == None:

                                        #     xlsx_file.writeCell(origin_point['row'], \
                                        #         origin_point['col'] + routing_avg["max_col"], "avg")

                                        # print(cal_route_avgs)
                                        # routing_avg["cal_route_avg"] = cal_route_avgs
                                        # for avg in cal_route_avgs:
                                        #     if avg:
                                        #         xlsx_file.writeCell(origin_point['row'] + cal_route_avgs.index(avg) + 1, \
                                        #             origin_point['col'] + routing_avg["max_col"], avg)

                            col_offset = 1
                            pass
                            
                    pass
                elif k == "Search":
                    pass
                            
#----------------------------------------------------------------------------------#                    
                # row_offset = 0
                # col_offset = 0 
                
                # # set list default
                # first_key = k.encode('utf-8')
                # sheet_data_attr.setdefault(first_key, {})
                # sheet_data_attr[first_key].setdefault('max_col', 0)
                # sheet_data_attr[first_key].setdefault('data_cnts', [])
                # sheet_data_attr[first_key].setdefault('total_times', [])
                # sheet_data_attr[first_key].setdefault('avg_times', [])
                # sheet_data_attr[first_key].setdefault('origin_point', {})
                # sheet_data_attr[first_key]["origin_point"]['col'] = origin_point['col']
                # sheet_data_attr[first_key]["origin_point"]['row'] = origin_point['row']
                
                # xlsx_file.writeCell(origin_point['row'] ,origin_point['col'], k)
                # col_offset += 1
                # row_offset += 1
                # index = 1

                # for k_1, v_1 in v.items():
                #     xlsx_file.writeCell(origin_point['row'] + row_offset,\
                #         origin_point['col'] - 1 + col_offset, index)
                #     index += 1
                #     for k_2, v_2 in v_1.items():
                #         beginTimes = []
                #         endTimes = []
                #         delta_times = []

                #         if k_2 == 'log point':
                #             match_logs1 = []
                #             match_logs2 = []
                #             if v_2['begin'] == '':        # search begin time in file logs
                #                 beginTimes.append(nav_log_file.beginTime())
                #             else:
                #                 search_begin_results = nav_log_file.searchLogs(v_2['begin'], "Message")

                #                 # begin_times = nav_log_file.getLogsTime(search_results)
                #                 if beginTimes:
                #                     beginTimes.sort()
                #                 else:
                #                     print(str(v_2['begin']) + ' is not found!')
                            
                #             if v_2['end'] == '':        # search end time in file logs
                #                 endTimes.append(nav_log_file.endTime())
                #             else:
                #                 search_end_results = nav_log_file.searchLogs(v_2['end'], "Message")

                #                 # end_times = nav_log_file.getLogsTime(search_results)
                #                 if endTimes:
                #                     endTimes.sort()
                #                 else:
                #                     print(str(v_2['end']) + ' is not found!')
                #             match_results = nav_log_file.resultMatching(search_begin_results, search_end_results)
                #             for match_result in match_results:
                #                 key = "Sending:  origin"
                #                 log = nav_log_file.searchLog(key, "Message", match_result["index"])
                #                 if log:

                #                     pass
                #                 else:
                #                     key = "Route request:"
                #                     log = nav_log_file.searchLog(key, "Message", match_result["index"])
                #                     if log:
                #                         pass
                #                     else:
                #                         continue
                                
                #             delta_times = nav_log_file.getDeltaTime(begin_times, end_times)
                            
                #             round_index = 0
                #             total_time = 0

                #             if delta_times:
                #                 for delta_time in delta_times:
                #                     round_index += 1
                #                     total_time = total_time + delta_time.total_seconds()
                                    
                #                     if len(delta_times) > 1:
                #                         # round_index += 1
                #                         if work_sheet.cell(origin_point['row'], origin_point['col'] + col_offset).value == None:
                #                             xlsx_file.writeCell(origin_point['row'],\
                #                                 origin_point['col'] + col_offset, "time cost(s)Round" + str(round_index))
                #                     else:
                #                         if work_sheet.cell(origin_point['row'], origin_point['col'] + col_offset).value == None:
                #                             xlsx_file.writeCell(origin_point['row'],\
                #                                 origin_point['col'] + col_offset, "time cost(s)Round")

                #                     xlsx_file.writeCell(origin_point['row'] + row_offset,\
                #                         origin_point['col'] + col_offset, delta_time.total_seconds())
                #                     col_offset += 1

                #             #save data count
                #             sheet_data_attr[first_key]["data_cnts"].append(round_index)
                #             # save total time
                #             sheet_data_attr[first_key]["total_times"].append(total_time)
                #             # save average time
                #             if round_index > 0:
                #                 sheet_data_attr[first_key]["avg_times"].append(round(total_time/round_index, 3))
                #             else:
                #                 sheet_data_attr[first_key]["avg_times"].append(None)

                #         else:   # <if k_2 == 'log point'>
                #             xlsx_file.writeCell(origin_point['row'] + row_offset,\
                #                 origin_point['col'] + col_offset, v_2)
                                    
                #             if work_sheet.cell(origin_point['row'], origin_point['col'] + col_offset).value == None:
                #                 xlsx_file.writeCell(origin_point['row'],\
                #                     origin_point['col'] + col_offset, k_2)  
                #             col_offset += 1

                #         # get max col
                #         if origin_point['col'] + col_offset > sheet_data_attr[first_key]['max_col']:
                #             sheet_data_attr[first_key]['max_col'] = origin_point['col'] + col_offset
                #     # location cell
                #     row_offset += 1
                #     col_offset -= (len(v_1) + len(delta_times) - 1)
                
                # origin_point['row'] = work_sheet.max_row + 3

            # add average and total colum
            # for k, v in sheet_data_attr.items():
            #     if k != "boot-up":
            #         index = 0
            #         while index < len(v['avg_times']):
            #             avg_time = v['avg_times'][index]
            #             if avg_time:
            #                 if work_sheet.cell(origin_point['row'], origin_point['col'] + col_offset).value == None:
            #                     xlsx_file.writeCell(v['origin_point']['row'], v['max_col'],\
            #                         'agv_times')
            #                 xlsx_file.writeCell(v['origin_point']['row'] + index + 1, v['max_col'],\
            #                     avg_time)
                            
            #             index += 1

            # add filter messages


            xlsx_file.resize(sheet_name)
    xlsx_file.create(xlsx_file_path)

