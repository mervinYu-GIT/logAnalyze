#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from os import path
import json  
from datetime import datetime
from argparse import ArgumentParser
import collections
from modules.navXlsx import NavXlsxFile
from modules.navLog import NavLogFile, NavLog
from modules.general_func import getFileList, sort_strings_with_embedded_numbers




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
                if k == "boot-up":
                    pass
                    boot_up = {}
                    if work_sheet.max_row == 1:
                        boot_up["row"] = work_sheet.max_row
                    else:
                        boot_up["row"] = work_sheet.max_row + 3

                    row_offset = 0
                    index = 0
                    xlsx_file.writeCell(boot_up["row"] , 1, k)
                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")
                        row_offset += 1
                        row = boot_up["row"] + row_offset

                        index += 1
                        xlsx_file.writeCell(row, 1, index)

                        col_offset = 1
                        for k_2, v_2 in v_1.items():
                            col_offset += 1
                            k_2 = k_2.encode("utf-8")
                            if k_2 == "process name":
                                if work_sheet.cell(boot_up["row"], \
                                        col_offset).value == None:
                                    xlsx_file.writeCell(boot_up["row"], \
                                        col_offset, k_2)

                                xlsx_file.writeCell(row, col_offset, v_2)

                            elif k_2 == "owner":
                                if work_sheet.cell(boot_up["row"], col_offset).value == None:
                                    xlsx_file.writeCell(boot_up["row"], col_offset, k_2)

                                xlsx_file.writeCell(row, col_offset, v_2)

                            elif k_2 == "log point":
                                begin_time = None
                                end_time = None
                                begin = v_2["begin"].encode("utf-8")
                                end = v_2["end"].encode("utf-8")


                                if begin:
                                    begin_result = nav_log.getLog(begin)
                                    if begin_result:
                                        begin_time = begin_result["time"]
                                else:
                                    begin_time = nav_log.getBeginTime()
                                
                                if end:
                                    end_result = nav_log.getLog(end)
                                    if end_result:
                                        end_time = end_result["time"]
                                else:
                                    end_time = nav_log.getEndTime()
                                
                                if work_sheet.cell(boot_up["row"], \
                                        col_offset).value == None:
                                    xlsx_file.writeCell(boot_up["row"], \
                                        col_offset, "time cost")

                                if begin_time and end_time:
                                    delta_time = end_time - begin_time

                                    xlsx_file.writeCell(row, \
                                        col_offset, delta_time.total_seconds())                          
          
                elif k == "Routing":
                    pass
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

                    if work_sheet.max_row == 1:
                        routing["row"] = work_sheet.max_row
                    else:
                        routing["row"] = work_sheet.max_row + 3

                    row_offset = 0
                    index = 0
                    xlsx_file.writeCell(routing["row"] , 1, k)
                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")

                        if k_1 == "Calculate Route":
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
                            for k_2, v_2 in v_1.items():
                                k_2 = k_2.encode("utf-8")
                                if k_2 == "process name":    # ----------process name --------------    
                                    routing["Calculate Guidance"]["process name"] = v_2.encode("utf-8")            

                                elif k_2 == "owner":        # -----------owner----------------------
                                    routing["Calculate Guidance"]["owner"] = v_2.encode("utf-8")            

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
                        while route_match_index < len(cal_route["matchs"]):
                            cur_route_match = cal_route["matchs"][route_match_index]
                            if route_match_index == len(cal_route["matchs"]) - 1:
                                if guidance_match["index"] > cur_route_match["index"]:
                                    guidance_match["name"] = cur_route_match["name"]
                                    break
                            else: 
                                next_route_match = cal_route["matchs"][route_match_index + 1]
                                if guidance_match["index"] > cur_route_match["index"] and \
                                    guidance_match["index"] < next_route_match["index"]:
                                    guidance_match["name"] = cur_route_match["name"]
                                    break
                            route_match_index += 1

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
                                if work_sheet.cell(routing["row"], group_col + route_index + 1).value == None:
                                    xlsx_file.writeCell(routing["row"], group_col + route_index + 1, "time cost(ms)Round" + str(route_index))
                            else:
                                if work_sheet.cell(routing["row"], group_col + route_index + 1).value == None:
                                    xlsx_file.writeCell(routing["row"], group_col + route_index + 1, "time cost(ms)Round")

                            xlsx_file.writeCell(cal_route_row + route_row_offset, \
                                group_col + route_index + 1, round(member["delta_time"].total_seconds(), 3))

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
                                if work_sheet.cell(routing["row"], group_col + guidance_index + 1).value == None:
                                    xlsx_file.writeCell(routing["row"], group_col + guidance_index + 1, "time cost(ms)Round" + str(guidance_index))
                            else:
                                if work_sheet.cell(routing["row"], group_col + guidance_index + 1).value == None:
                                    xlsx_file.writeCell(routing["row"], group_col + guidance_index + 1, "time cost(ms)Round")

                            xlsx_file.writeCell(cal_guidance_row + guidance_row_offset, \
                                group_col + guidance_index + 1, round(member["delta_time"].total_seconds(), 3))

                        guidance_row_offset += 1
                        
                        if routing["max_col"] < group_col + guidance_index:
                            routing["max_col"] = group_col + guidance_index  

                    avg_col = col_offset + 1
                    avg_row_offset = 0
                    
                    xlsx_file.writeCell(routing["row"], avg_col, "average time cost(ms)")
                    for k_route_group, v_route_group in route_group.items():
                        avg_cnt = 0
                        avg_total = 0
                        if len(v_route_group) > 1:
                            for member in v_route_group:
                                avg_total += member["delta_time"].total_seconds()
                                avg_cnt += 1
                            avg = round(avg_total / avg_cnt, 3)
                            xlsx_file.writeCell(cal_route_row + avg_row_offset, avg_col, avg)
                        avg_row_offset += 1

                    avg_row_offset = 0
                    for k_guidance_group, v_guidance_group in guidance_group.items():
                        avg_cnt = 0
                        avg_total = 0
                        if len(v_guidance_group) > 1:
                            for member in v_guidance_group:
                                avg_total += member["delta_time"].total_seconds()
                                avg_cnt += 1
                            avg = round(avg_total / avg_cnt, 3)
                            xlsx_file.writeCell(cal_guidance_row + avg_row_offset, avg_col, avg)
                        avg_row_offset += 1

                   
                elif k == "Search":
                    search = {}
                    search["row"] = 0
                    search["max_col"] = 0
                    search["object"] = collections.OrderedDict()

                    if work_sheet.max_row == 1:
                        search["row"] = work_sheet.max_row
                    else:
                        search["row"] = work_sheet.max_row + 3
                    pass

                    row_offset = 0
                    index = 0
                    xlsx_file.writeCell(search["row"] , 1, k)  # write cell "search"

                    for k_1, v_1 in v.items():
                        search["object"][k_1] = {}
                        search["object"][k_1] = collections.OrderedDict()
                        search["object"][k_1]["group"] = collections.OrderedDict()
                        search["object"][k_1]["group"]["total"] = {}
                        search["object"][k_1]["group"]["total"]["matchs"] = []
                        search["object"][k_1]["group"]["total"]["avg"] = 0
                        cur_col = 1
                        k_1 = k_1.encode("utf-8")
                        row_offset += 1
                        index += 1
                        xlsx_file.writeCell(search["row"] + row_offset, 1, index)

                        for k_2, v_2 in v_1.items():
                            k_2 = k_2.encode("utf-8")
                            cur_col += 1
                            
                            if k_2 == "process name":
                                if work_sheet.cell(search["row"], cur_col).value == None:
                                        xlsx_file.writeCell(search["row"], cur_col, k_2)
                                xlsx_file.writeCell(search["row"] + row_offset, cur_col, v_2)

                                pass
                            elif k_2 == "owner":
                                if work_sheet.cell(search["row"], cur_col).value == None:
                                        xlsx_file.writeCell(search["row"], cur_col, k_2)
                                xlsx_file.writeCell(search["row"] + row_offset, cur_col, v_2)

                                pass
                            elif k_2 == "log point":
                                begin_logs = []
                                end_logs = []
                                begin = v_2["begin"].encode("utf_8")
                                end = v_2["end"].encode("utf-8")

                                if begin:
                                        begin_logs = nav_log.getLogs(begin)
                                else:
                                    continue
                                
                                if end:
                                    end_logs = nav_log.getLogs(end)
                                else:
                                    continue

                                if begin_logs and end_logs:   # get total matchs
                                    index1 = 0
                                    index2 = 0
                                    
                                    while index1 < len(begin_logs) and index2 < len(end_logs):
                                        match = {}
                                        match["index"] = 0
                                        match["begin_index"] = 0
                                        match["end_index"] = 0
                                        match["delta_time"] = None
                                        match["begin_message"] = ""
                                        match["end_message"] = ""
                                        begin_index = begin_logs[index1]["index"]
                                        end_index = end_logs[index2]["index"]

                                        if begin_index >= end_index:
                                            index2 += 1
                                            continue
                                        else:
                                            if index1 != len(begin_logs) - 1:
                                                next_begin_index = begin_logs[index1 + 1]["index"]
                                            else:
                                                match["begin_index"] = begin_logs[index1]["index"]
                                                match["end_index"] = end_logs[index2]["index"]
                                                match["index"] = begin_logs[index1]["index"]          # get match "index"
                                                delta_time = end_logs[index2]["time"] - begin_logs[index1]["time"]
                                                match["delta_time"] = round(delta_time.total_seconds(), 3)     # get match "delta_time"
                        
                                                search["object"][k_1]["group"]["total"]["matchs"].append(match)
                                                break
                                            if next_begin_index < end_index:
                                                index1 += 1
                                                continue
                                            else:
                                                match["begin_index"] = begin_logs[index1]["index"]
                                                match["end_index"] = end_logs[index2]["index"]
                                                match["index"] = begin_logs[index1]["index"]          # get match "index"
                                                delta_time = end_logs[index2]["time"] - begin_logs[index1]["time"]
                                                match["delta_time"] = round(delta_time.total_seconds(), 3)      # get match "delta_time"

                                                search["object"][k_1]["group"]["total"]["matchs"].append(match)
                                                index1 += 1
                                                index2 += 2

                                if search["object"][k_1]["group"]["total"]["matchs"]:
                                    for match in search["object"][k_1]["group"]["total"]["matchs"]:
                                        # onebox log
                                        onebox_log = nav_log.getLog("OneBoxSearchFlow send query", match["begin_index"], match["end_index"] + 1)
                                        if onebox_log:
                                            if search["object"][k_1]["group"].has_key("onebox"):
                                                search["object"][k_1]["group"]["onebox"]["matchs"].append(match)
                                            else:
                                                search["object"][k_1]["group"]["onebox"] = {}
                                                search["object"][k_1]["group"]["onebox"]["matchs"] = []
                                                search["object"][k_1]["group"]["onebox"]["matchs"].append(match)
                                        
                                        # category log
                                        # suggestion log
                                       
                                # delta time average
                                for k, v in search["object"][k_1]["group"].items():
                                    group_match_cnt = 0
                                    group_total_delta = 0
                                    for match in v["matchs"]:           
                                        group_total_delta += match["delta_time"]
                                        group_match_cnt += 1
                                    if group_total_delta != 0 and group_match_cnt != 0:
                                        v["avg"] = round(group_total_delta/group_match_cnt, 3)
                                    else:
                                        v["avg"] = None

                        if work_sheet.cell(search["row"], cur_col).value == None:
                            xlsx_file.writeCell(search["row"], cur_col, "group")
                        if work_sheet.cell(search["row"], cur_col+1).value == None:
                            xlsx_file.writeCell(search["row"], cur_col+1, "average time cost(ms)")
                        for k, v in search["object"][k_1]["group"].items():
                            # default matchs
                            if v["matchs"]:
                                xlsx_file.writeCell(search["row"]+row_offset, cur_col, k)
                                xlsx_file.writeCell(search["row"] + row_offset, cur_col + 1, v["avg"])
                                default_group_cnt = 0
                                for match in v["matchs"]:
                                    default_group_cnt += 1
                                    if work_sheet.cell(search["row"], cur_col + default_group_cnt + 1).value == None:
                                        xlsx_file.writeCell(search["row"], cur_col + default_group_cnt + 1, "time cost(ms)Round" + str(default_group_cnt))
                                    xlsx_file.writeCell(search["row"] + row_offset, cur_col + default_group_cnt + 1, match["delta_time"])
                                if search["max_col"] < cur_col + default_group_cnt:
                                    search["max_col"] = cur_col + default_group_cnt
                            row_offset += 1
                        row_offset -= 1

                else:
                    pass
                    
            xlsx_file.resize(sheet_name)
    xlsx_file.create(xlsx_file_path)

