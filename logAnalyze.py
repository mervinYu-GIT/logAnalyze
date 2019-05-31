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
                # print("k = " + k)
                # print(type(k))
                if k == "boot-up":
                    # print('in ' + k)
                    boot_up = {}
                    boot_up["row"] = 1

                    index = 0
                    # row_offset = 0
                    xlsx_file.writeCell(boot_up["row"] , 1, k)
                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")
                        # print("k1 = " + k_1)
                        if k_1 == "loading libfordhal.so":
                            # print("in " + k_1)
                            index += 1
                            libfordhal_row = boot_up["row"] + index
                            xlsx_file.writeCell(libfordhal_row, 1, index)

                            col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(libfordhal_row, \
                                        col_offset, v_2)

                                elif k_2 == "owner":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(libfordhal_row, \
                                        col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")


                                    if begin:
                                        begin_result = nav_log.getLog(begin)
                                        if begin_result:
                                            # time_str = begin_result["log"].split("|")[1]
                                            begin_time = begin_result["time"]
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_result = nav_log.getLog(end)
                                        if end_result:
                                            # time_str = end_result["log"].split("|")[1]
                                            end_time = end_result["time"]
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, "time cost")

                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time

                                        xlsx_file.writeCell(libfordhal_row, \
                                            col_offset, delta_time.total_seconds())                          
                        elif k_1 == "loading FHC":
                            # print("in " + k_1)
                            index += 1
                            fhc_row = boot_up["row"] + index
                            xlsx_file.writeCell(fhc_row, 1, index)

                            col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(fhc_row, \
                                        col_offset, v_2)

                                elif k_2 == "owner":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(fhc_row, \
                                        col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")


                                    if begin:
                                        begin_result = nav_log.getLog(begin)
                                        if begin_result:
                                            # time_str = begin_result["log"].split("|")[1]
                                            begin_time = begin_result["time"]
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_result = nav_log.getLog(end)
                                        if end_result:
                                            # time_str = end_result["log"].split("|")[1]
                                            end_time = end_result["time"]
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, "time cost")

                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time

                                        xlsx_file.writeCell(fhc_row, \
                                            col_offset, delta_time.total_seconds())
                        elif k_1 == "loading libqtarp.so":
                            # print("in " + k_1)
                            index += 1
                            qtarp_row = boot_up["row"] + index
                            xlsx_file.writeCell(qtarp_row, 1, index)

                            col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(qtarp_row, \
                                        col_offset, v_2)

                                elif k_2 == "owner":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(qtarp_row, \
                                        col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")


                                    if begin:
                                        begin_result = nav_log.getLog(begin)
                                        if begin_result:
                                            # time_str = begin_result["log"].split("|")[1]
                                            begin_time = begin_result["time"]
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_result = nav_log.getLog(end)
                                        if end_result:
                                            # time_str = end_result["log"].split("|")[1]
                                            end_time = end_result["time"]
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, "time cost")

                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time

                                        xlsx_file.writeCell(qtarp_row, \
                                            col_offset, delta_time.total_seconds())
                        elif k_1 == "FordHAL Init":
                            # print("in " + k_1)
                            index += 1
                            ford_init_row = boot_up["row"] + index
                            xlsx_file.writeCell(ford_init_row, 1, index)

                            col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(ford_init_row, \
                                        col_offset, v_2)

                                elif k_2 == "owner":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(ford_init_row, \
                                        col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")


                                    if begin:
                                        begin_result = nav_log.getLog(begin)
                                        if begin_result:
                                            # time_str = begin_result["log"].split("|")[1]
                                            begin_time = begin_result["time"]
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_result = nav_log.getLog(end)
                                        if end_result:
                                            # time_str = end_result["log"].split("|")[1]
                                            end_time = end_result["time"]
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, "time cost")

                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time

                                        xlsx_file.writeCell(ford_init_row, \
                                            col_offset, delta_time.total_seconds())
                        elif k_1 == "loading QML":
                            # print("in " + k_1)
                            index += 1
                            loading_qml_row = boot_up["row"] + index
                            xlsx_file.writeCell(loading_qml_row, 1, index)

                            col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(loading_qml_row, \
                                        col_offset, v_2)

                                elif k_2 == "owner":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(loading_qml_row, \
                                        col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")


                                    if begin:
                                        begin_result = nav_log.getLog(begin)
                                        if begin_result:
                                            # time_str = begin_result["log"].split("|")[1]
                                            begin_time = begin_result["time"]
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_result = nav_log.getLog(end)
                                        if end_result:
                                            # time_str = end_result["log"].split("|")[1]
                                            end_time = end_result["time"]
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, "time cost")

                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time

                                        xlsx_file.writeCell(loading_qml_row, \
                                            col_offset, delta_time.total_seconds())
                            pass
                        elif k_1 == "SDK Init":
                            # print("in " + k_1)
                            index += 1
                            sdk_init_row = boot_up["row"] + index
                            xlsx_file.writeCell(sdk_init_row, 1, index)

                            col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(sdk_init_row, \
                                        col_offset, v_2)

                                elif k_2 == "owner":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(sdk_init_row, \
                                        col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")


                                    if begin:
                                        begin_result = nav_log.getLog(begin)
                                        if begin_result:
                                            # time_str = begin_result["log"].split("|")[1]
                                            begin_time = begin_result["time"]
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_result = nav_log.getLog(end)
                                        if end_result:
                                            # time_str = end_result["log"].split("|")[1]
                                            end_time = end_result["time"]
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, "time cost")

                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time

                                        xlsx_file.writeCell(sdk_init_row, \
                                            col_offset, delta_time.total_seconds())
                        elif k_1 == "Loading HMI":   
                            # print("in " + k_1)
                            index += 1
                            loading_hmi_row = boot_up["row"] + index
                            xlsx_file.writeCell(loading_hmi_row, 1, index)

                            col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(loading_hmi_row, \
                                        col_offset, v_2)

                                elif k_2 == "owner":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(loading_hmi_row, \
                                        col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")


                                    if begin:
                                        begin_result = nav_log.getLog(begin)
                                        if begin_result:
                                            # time_str = begin_result["log"].split("|")[1]
                                            begin_time = begin_result["time"]
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_result = nav_log.getLog(end)
                                        if end_result:
                                            # time_str = end_result["log"].split("|")[1]
                                            end_time = end_result["time"]
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, "time cost")

                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time

                                        xlsx_file.writeCell(loading_hmi_row, \
                                            col_offset, delta_time.total_seconds())
                        elif k_1 == "total":
                            # print("in " + k_1)
                            index += 1
                            total_row = boot_up["row"] + index
                            xlsx_file.writeCell(total_row, 1, index)

                            col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(total_row, \
                                        col_offset, v_2)

                                elif k_2 == "owner":
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, k_2)

                                    xlsx_file.writeCell(total_row, \
                                        col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_time = None
                                    end_time = None
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")


                                    if begin:
                                        begin_result = nav_log.getLog(begin)
                                        if begin_result:
                                            # time_str = begin_result["log"].split("|")[1]
                                            begin_time = begin_result["time"]
                                    else:
                                        begin_time = nav_log.getBeginTime()
                                    
                                    if end:
                                        end_result = nav_log.getLog(end)
                                        if end_result:
                                            # time_str = end_result["log"].split("|")[1]
                                            end_time = end_result["time"]
                                    else:
                                        end_time = nav_log.getEndTime()
                                    
                                    col_offset += 1
                                    if work_sheet.cell(boot_up["row"], \
                                         col_offset).value == None:
                                        xlsx_file.writeCell(boot_up["row"], \
                                            col_offset, "time cost")

                                    if begin_time and end_time:
                                        delta_time = end_time - begin_time

                                        xlsx_file.writeCell(total_row, \
                                            col_offset, delta_time.total_seconds())
                       
                elif k == "Routing":
                    routing = {}  # routing message
                    routing["row"] = 0
                    routing["max_col"] = 0

                    routing["Calculate Route"] = {}
                    routing["Calculate Route"]["group"] = collections.OrderedDict()
                    routing["Calculate Route"]["row"] = 0
                    routing["Calculate Route"]["begin"] = ""
                    routing["Calculate Route"]["end"] = ""
                    routing["Calculate Route"]["matchs"] = []
                    routing["Calculate Route"]["process name"] = ""
                    routing["Calculate Route"]["owner"] = ""

                    routing["Calculate Guidance"] = {}
                    routing["Calculate Guidance"]["group"] = collections.OrderedDict()
                    routing["Calculate Guidance"]["row"] = 0
                    routing["Calculate Guidance"]["begin"] = ""
                    routing["Calculate Guidance"]["end"] = ""
                    routing["Calculate Guidance"]["matchs"] = []
                    routing["Calculate Guidance"]["process name"] = ""
                    routing["Calculate Guidance"]["owner"] = ""

                    # origin_point["row"] = work_sheet.max_row + 3
                    routing["row"] = work_sheet.max_row + 3
                    row_offset = 0
                    index = 0
                    # col_offset = 0 
                    # routing_avg = {"max_col":0}

                    xlsx_file.writeCell(routing["row"] , 1, k)
                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")

                        if k_1 == "Calculate Route":
                            # routing["Calculate Route"] = routing["row"] + row_offset
                            row_offset += 1
                            routing["Calculate Route"]["row"] = routing["row"] + row_offset
                            cal_route_row = routing["Calculate Route"]["row"]
                            
                            index += 1
                            xlsx_file.writeCell(cal_route_row, 1, index)

                            col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":    # ----------process name --------------                 
                                    col_offset += 1
                                    if work_sheet.cell(routing["row"], col_offset).value == None:
                                        xlsx_file.writeCell(routing["row"], col_offset, k_2)

                                    xlsx_file.writeCell(cal_route_row, \
                                         col_offset, v_2)
                                elif k_2 == "owner":        # -----------owner----------------------
                                    col_offset += 1
                                    if work_sheet.cell(routing["row"], col_offset).value == None:
                                        xlsx_file.writeCell(routing["row"], col_offset, k_2)

                                    xlsx_file.writeCell(cal_route_row, \
                                         col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_logs = []
                                    end_logs = []
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")

                                    routing["Calculate Route"]["begin"] = begin
                                    routing["Calculate Route"]["end"] = end
                                    
                                    if begin:
                                        begin_logs = nav_log.getLogs(begin)
                                    else:
                                        continue
                                    
                                    if end:
                                        end_logs = nav_log.getLogs(end)
                                    else:
                                        continue

                                    if begin_logs and end_logs:
                                        index1 = 0
                                        index2 = 0
                                        matchs = []
                                        while index1 < len(begin_logs) and index2 < len(end_logs):
                                            match = {}
                                            match["index"] = 0
                                            match["name"] = ""
                                            match["delta_time"] = None
                                            begin_index = begin_logs[index1]["index"]
                                            end_index = end_logs[index2]["index"]

                                            if begin_index >= end_index:
                                                index2 += 1
                                                continue
                                            else:
                                                if index1 != len(begin_logs) - 1:
                                                    next_begin_index = begin_logs[index1 + 1]["index"]
                                                else:
                                                    match["index"] = begin_logs[index1]["index"]          # get match "index"
                                                    delta_time = end_logs[index2]["time"] - begin_logs[index1]["time"]
                                                    match["delta_time"] = delta_time                      # get match "delta_time"

                                                    key = "Sending:  origin"
                                                    begin_index = match["index"]
                                                    end_index = end_logs[index2]["index"]
                                                    result = nav_log.getLog(key, begin_index, end_index)
                                                    if result:
                                                        msg = result["message"]
                                                        search_point_begin = msg.index("formatted_address:")
                                                        dst_name = msg[msg.index("\"", search_point_begin) + 1:msg.index("\n", search_point_begin) - 1]
                                                        match["name"] = dst_name                  # get match "name"

                                                    else:
                                                        key = "Route request:"
                                                        result = nav_log.getLog(key, begin_index, end_index)
                                                        if result:
                                                            msg = result["message"]
                                                            search_point_begin = msg.index("formatted_address:")
                                                            dst_name = msg[msg.index("\"", search_point_begin) + 1:msg.index("\n", search_point_begin) - 1]
                                                            match["name"] = dst_name             # get match "name"
                                                        else:
                                                            match["name"] = None                   # if no result, set None

                                                    matchs.append(match)

                                                    break
                                                if next_begin_index < end_index:
                                                    index1 += 1
                                                    continue
                                                else:
                                                    match["index"] = begin_logs[index1]["index"]          # get match "index"
                                                    delta_time = end_logs[index2]["time"] - begin_logs[index1]["time"]
                                                    match["delta_time"] = delta_time                      # get match "delta_time"

                                                    key = "Sending:  origin"
                                                    begin_index = match["index"]
                                                    end_index = end_logs[index2]["index"]
                                                    result = nav_log.getLog(key, begin_index, end_index)
                                                    if result:
                                                        msg = result["message"]
                                                        search_point_begin = msg.index("formatted_address:")
                                                        dst_name = msg[msg.index("\"", search_point_begin) + 1:msg.index("\n", search_point_begin) - 1]
                                                        match["name"] = dst_name                  # get match "name"

                                                    else:
                                                        key = "Route request:"
                                                        result = nav_log.getLog(key, begin_index, end_index)
                                                        if result:
                                                            msg = result["message"]
                                                            search_point_begin = msg.index("formatted_address:")
                                                            dst_name = msg[msg.index("\"", search_point_begin) + 1:msg.index("\n", search_point_begin) - 1]
                                                            match["name"] = dst_name             # get match "name"
                                                        else:
                                                            match["name"] = None                   # if no result, set None

                                                    matchs.append(match)
                                                    index1 += 1
                                                    index2 += 2
                                        # print(matchs)
                                        routing["Calculate Route"]["matchs"] = matchs
              
                        elif k_1 == "Calculate Guidance":
                            # row_offset += 1
                            # routing["Calculate Guidance"]["row"] = routing["row"] + row_offset
                            # cal_guidance_row = routing["Calculate Guidance"]["row"]
                            
                            # index += 1
                            # xlsx_file.writeCell(cal_guidance_row, 1, index)

                            # col_offset = 1
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":    # ----------process name --------------    
                                    routing["Calculate Guidance"]["process name"] = v_2.encode("utf-8")            
                                    # col_offset += 1
                                    # if work_sheet.cell(routing["row"], col_offset).value == None:
                                    #     xlsx_file.writeCell(routing["row"], col_offset, k_2)

                                    # xlsx_file.writeCell(cal_guidance_row, \
                                    #      col_offset, v_2)

                                elif k_2 == "owner":        # -----------owner----------------------
                                    routing["Calculate Guidance"]["owner"] = v_2.encode("utf-8")            

                                    # col_offset += 1
                                    # if work_sheet.cell(routing["row"], col_offset).value == None:
                                    #     xlsx_file.writeCell(routing["row"], col_offset, k_2)

                                    # xlsx_file.writeCell(cal_guidance_row, \
                                    #      col_offset, v_2)

                                elif k_2 == "log point":
                                    begin_logs = []
                                    end_logs = []
                                    begin = v_2["begin"].encode("utf-8")
                                    end = v_2["end"].encode("utf-8")

                                    routing["Calculate Guidance"]["begin"] = begin
                                    routing["Calculate Guidance"]["end"] = end
                                    
                                    if begin:
                                        begin_logs = nav_log.getLogs(begin)
                                    else:
                                        continue
                                    
                                    if end:
                                        end_logs = nav_log.getLogs(end)
                                    else:
                                        continue

                                    if begin_logs and end_logs:
                                        index1 = 0
                                        index2 = 0
                                        matchs = []
                                        while index1 < len(begin_logs) and index2 < len(end_logs):
                                            match = {}
                                            match["index"] = 0
                                            match["name"] = ""
                                            match["delta_time"] = None
                                            begin_index = begin_logs[index1]["index"]
                                            end_index = end_logs[index2]["index"]

                                            if begin_index >= end_index:
                                                index2 += 1
                                                continue
                                            else:
                                                if index1 != len(begin_logs) - 1:
                                                    next_begin_index = begin_logs[index1 + 1]["index"]
                                                else:
                                                    match["index"] = begin_logs[index1]["index"]          # get match "index"
                                                    delta_time = end_logs[index2]["time"] - begin_logs[index1]["time"]
                                                    match["delta_time"] = delta_time                      # get match "delta_time"
                          
                                                    matchs.append(match)
                                                    break
                                                if next_begin_index < end_index:
                                                    index1 += 1
                                                    continue
                                                else:
                                                    match["index"] = begin_logs[index1]["index"]          # get match "index"
                                                    delta_time = end_logs[index2]["time"] - begin_logs[index1]["time"]
                                                    match["delta_time"] = delta_time                      # get match "delta_time"

                                                    matchs.append(match)
                                                    index1 += 1
                                                    index2 += 2
                                        routing["Calculate Guidance"]["matchs"] = matchs
                    
                    cal_route = routing["Calculate Route"]
                    cal_guidance = routing["Calculate Guidance"]
                    
                    for guidance_match in cal_guidance["matchs"]:
                        route_match_index = 0
                        while route_match_index < len(cal_route["matchs"]) - 1:
                            cur_route_match = cal_route["matchs"][route_match_index]
                            next_route_match = cal_route["matchs"][route_match_index + 1]
                            if guidance_match["index"] > cur_route_match["index"] and \
                                guidance_match["index"] < next_route_match["index"]:
                                guidance_match["name"] = cur_route_match["name"]
                                break
                            route_match_index += 1
                    
                    # print(cal_route)
                    # print(cal_guidance)
                    # groups
                    cal_route_matchs = cal_route["matchs"]
                    cal_guidance_matchs = cal_guidance["matchs"]
                    
                    route_group = cal_route["group"]
                    for match in cal_route_matchs:
                        if route_group.has_key(match["name"]):
                            route_group[match["name"]].append(match)
                        else:
                            route_group[match["name"]] = []
                            route_group[match["name"]].append(match)

                    guidance_group = cal_guidance["group"]
                    for match in cal_guidance_matchs:
                        if guidance_group.has_key(match["name"]):
                            guidance_group[match["name"]].append(match)
                        else:
                            guidance_group[match["name"]] = []
                            guidance_group[match["name"]].append(match)

                    

#########################  debug ##########################################
                    # print(route_group)
                    print("-------------------------------------------------------------------")
                    for k,v in route_group.items():
                        print(k)
                        for member in v:
                            print(member["index"])
                        print("--------------------------------")
                    # print(guidance_group)
                    print("--------------------------------------------------------------------")
                    for k,v in guidance_group.items():
                        print(k)
                        for member in v:
                            print(member["index"])
                        print("--------------------------------")
                    print("-------------------------------------------------------------------")
                    print("cal_route_row: " + str(cal_route_row))
                    # print("cal_guidance_row: " + str(cal_guidance_row))
                    print("col_offset: " + str(col_offset))
######################### debug ###########################################
                    col_offset += 1
                    group_col = col_offset
                    route_row_offset = 0
                    xlsx_file.writeCell(routing["row"], col_offset, "group")
                    for k_route_group, v_route_group in route_group.items():
                        route_index = 0
                        xlsx_file.writeCell(cal_route_row + route_row_offset, group_col, k_route_group)
                        for member in v_route_group:
                            route_index += 1
                            if len(v_route_group) > 1:
                                if work_sheet.cell(routing["row"], group_col + route_index).value == None:
                                    xlsx_file.writeCell(routing["row"], group_col + route_index, "time cost(ms)Round" + str(route_index))
                            else:
                                if work_sheet.cell(routing["row"], group_col + route_index).value == None:
                                    xlsx_file.writeCell(routing["row"], group_col + route_index, "time cost(ms)Round")

                            xlsx_file.writeCell(cal_route_row + route_row_offset, \
                                group_col + route_index, round(member["delta_time"].total_seconds(), 3))

                        route_row_offset += 1
                        
                        if routing["max_col"] < group_col + route_index:
                            routing["max_col"] = group_col + route_index

                    cal_guidance_row = cal_route_row + route_row_offset
                    index += 1
                    xlsx_file.writeCell(cal_guidance_row, 1, index)
                    xlsx_file.writeCell(cal_guidance_row, 2, routing["Calculate Guidance"]["process name"])
                    xlsx_file.writeCell(cal_guidance_row, 3, routing["Calculate Guidance"]["owner"])
                    guidance_row_offset = 0
                    for k_guidance_group, v_guidance_group in guidance_group.items():
                        guidance_index = 0
                        xlsx_file.writeCell(cal_guidance_row + guidance_row_offset, group_col, k_guidance_group)
                        for member in v_guidance_group:
                            guidance_index += 1
                            if len(v_guidance_group) > 1:
                                if work_sheet.cell(routing["row"], group_col + guidance_index).value == None:
                                    xlsx_file.writeCell(routing["row"], group_col + guidance_index, "time cost(ms)Round" + str(guidance_index))
                            else:
                                if work_sheet.cell(routing["row"], group_col + guidance_index).value == None:
                                    xlsx_file.writeCell(routing["row"], group_col + guidance_index, "time cost(ms)Round")

                            xlsx_file.writeCell(cal_guidance_row + guidance_row_offset, \
                                group_col + guidance_index, round(member["delta_time"].total_seconds(), 3))

                        guidance_row_offset += 1
                        
                        if routing["max_col"] < group_col + guidance_index:
                            routing["max_col"] = group_col + guidance_index  

################################################# debug ################################
                    print(routing["max_col"])  
################################################# debug ################################
                    agv_col = routing["max_col"] + 1
                    agv_row_offset = 0
                    xlsx_file.writeCell(routing["row"], agv_col, "agv")
                    for k_route_group, v_route_group in route_group.items():
                        agv_cnt = 0
                        agv_total = 0
                        if len(v_route_group) > 1:
                            for member in v_route_group:
                                agv_total += member["delta_time"].total_seconds()
                                agv_cnt += 1
                            agv = round(agv_total / agv_cnt, 3)
                            xlsx_file.writeCell(cal_route_row + agv_row_offset, agv_col, agv)
                        agv_row_offset += 1

                    agv_row_offset = 0
                    for k_guidance_group, v_guidance_group in guidance_group.items():
                        agv_cnt = 0
                        agv_total = 0
                        if len(v_guidance_group) > 1:
                            for member in v_guidance_group:
                                agv_total += member["delta_time"].total_seconds()
                                agv_cnt += 1
                            agv = round(agv_total / agv_cnt, 3)
                            xlsx_file.writeCell(cal_guidance_row + agv_row_offset, agv_col, agv)
                        agv_row_offset += 1

                   
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

