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
from modules.navLog import NavLog
from modules.general_func import getFileList, sort_strings_with_embedded_numbers


category = {
    "-1":"Recents",
    "-2":"Saved",
    "-3":"Trips",
    "161":"camping_sites",
    "101":"GasStations",
    "1000":"Food",
    "471":"Attractions",
    "129":"Parking",
    "201":"ATMs",
    "1003":"Shopping",
    "171":"RestAreas",
    "11":"Coffee",
    "645":"Emergency",
    "111":"Hotel"
}

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

            root = collections.OrderedDict()      # global data

            for k, v in json_data.items():
                k = k.encode("utf-8")
                first_title = k
                if k == "boot-up":
                    pass
                    boot_up = {}
                    boot_up["cell_point"] = {}
                    boot_up["cell_point"]["left_up"] = {}
                    boot_up["cell_point"]["right_down"] = {}
                    if work_sheet.max_row == 1:
                        boot_up["cell_point"]["left_up"]["row"] = work_sheet.max_row
                    else:
                        boot_up["cell_point"]["left_up"]["row"] = work_sheet.max_row + 3
                    boot_up["cell_point"]["left_up"]["col"] = 1
                    boot_up["cell_point"]["right_down"]["col"] = 0

                    row_offset = 0
                    index = 0
                    xlsx_file.writeCell(boot_up["cell_point"]["left_up"]["row"] , 1, k)
                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")
                        second_title = k_1
                        row_offset += 1
                        row = boot_up["cell_point"]["left_up"]["row"] + row_offset

                        index += 1
                        xlsx_file.writeCell(row, 1, index)

                        col_offset = 1
                        for k_2, v_2 in v_1.items():
                            col_offset += 1
                            k_2 = k_2.encode("utf-8")
                            if k_2 == "process name":
                                if work_sheet.cell(boot_up["cell_point"]["left_up"]["row"], col_offset).value == None:
                                    xlsx_file.writeCell(boot_up["cell_point"]["left_up"]["row"], col_offset, k_2)

                                xlsx_file.writeCell(row, col_offset, v_2)

                            elif k_2 == "owner":
                                if work_sheet.cell(boot_up["cell_point"]["left_up"]["row"], col_offset).value == None:
                                    xlsx_file.writeCell(boot_up["cell_point"]["left_up"]["row"], col_offset, k_2)

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
                                
                                if work_sheet.cell(boot_up["cell_point"]["left_up"]["row"], \
                                        col_offset).value == None:
                                    xlsx_file.writeCell(boot_up["cell_point"]["left_up"]["row"], \
                                        col_offset, "time cost")

                                if begin_time and end_time:
                                    delta_time = end_time - begin_time

                                    xlsx_file.writeCell(row, \
                                        col_offset, delta_time.total_seconds())

                        if boot_up["cell_point"]["right_down"]["col"] < col_offset:
                            boot_up["cell_point"]["right_down"]["col"] = col_offset

                    boot_up["cell_point"]["right_down"]["row"] = boot_up["cell_point"]["left_up"]["row"] + row_offset
                    xlsx_file.setCellBorder(sheet_name, boot_up["cell_point"]["left_up"]["row"],
                                                        boot_up["cell_point"]["left_up"]["col"],
                                                        boot_up["cell_point"]["right_down"]["row"],
                                                        boot_up["cell_point"]["right_down"]["col"],
                                                        )
          
                elif k == "Routing":
                    pass
                    routing = {}  # routing message
                    routing["cell_point"] = {}
                    routing["cell_point"]["left_up"] = {}
                    routing["cell_point"]["right_down"] = {}
                    routing["cell_point"]["right_down"]["row"] = 1
                    routing["cell_point"]["right_down"]["col"] = 1

                    routing["process"] = collections.OrderedDict()

                    if work_sheet.max_row == 1:
                        routing["cell_point"]["left_up"]["row"] = work_sheet.max_row
                    else:
                        routing["cell_point"]["left_up"]["row"] = work_sheet.max_row + 3
                    routing["cell_point"]["left_up"]["col"] = 1

                    row_offset = 0
                    cur_row = routing["cell_point"]["left_up"]["row"]
                    cur_col = 1
                    index = 0
                    xlsx_file.writeCell(routing["cell_point"]["left_up"]["row"] , 1, k)

                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")
                        begin_logs = []
                        end_logs = []
                        begin = v_1["log point"]["begin"].encode("utf-8")
                        end = v_1["log point"]["end"].encode("utf-8")
                        
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
                                begin_index = begin_logs[index1]["index"]
                                end_index = end_logs[index2]["index"]

                                if begin_index >= end_index:
                                    index2 += 1
                                    continue
                                else:
                                    if index1 != len(begin_logs) - 1:
                                        next_begin_index = begin_logs[index1 + 1]["index"]
                                    else:
                                        match["begin_index"] = begin_logs[index1]["index"]          # get match "index"
                                        match["end_index"] = end_logs[index2]["index"]
                                        match["delta_time"] = end_logs[index2]["time"] - begin_logs[index1]["time"]  # get match "delta_time"

                                        matchs.append(match)

                                        break
                                    if next_begin_index < end_index:
                                        index1 += 1
                                        continue
                                    else:
                                        match["begin_index"] = begin_logs[index1]["index"]          # get match "index"
                                        match["end_index"] = end_logs[index2]["index"]
                                        match["delta_time"] = end_logs[index2]["time"] - begin_logs[index1]["time"]  # get match "delta_time"                                                             

                                        matchs.append(match)
                                        index1 += 1
                                        index2 += 2
                            if routing["process"].has_key(k_1):
                                routing["process"][k_1]["matchs"] = []
                                routing["process"][k_1]["matchs"] = matchs[:]
                            else:
                                routing["process"][k_1] = {}
                                routing["process"][k_1]["matchs"] = matchs[:]

                    if routing["process"] and routing["process"]["Calculate Route"]\
                                          and routing["process"]["Calculate Route"]["matchs"]:
                        search_key = "Sending:  origin"
                        cal_route_index = 0
                        cal_route_matchs = routing["process"]["Calculate Route"]["matchs"][:]
                        while cal_route_index < len(cal_route_matchs):
                            cur_route_match = cal_route_matchs[cal_route_index]
                            if cal_route_index == len(cal_route_matchs) - 1:
                                result = nav_log.getLog(search_key, cur_route_match["begin_index"])
                                if not result:
                                    search_key = "Route request:"
                                    result = nav_log.getLog(search_key, cur_route_match["begin_index"])
                                    
                            else:
                                next_match = cal_route_matchs[cal_route_index + 1]
                                result = result = nav_log.getLog(search_key, cur_route_match["begin_index"], next_match["end_index"])
                                if not result:
                                    search_key = "Route request:"
                                    result = nav_log.getLog(search_key, cur_route_match["begin_index"], next_match["end_index"])

                            if result:
                                msg = result["message"]
                                search_point_begin = msg.index("formatted_address:")
                                dst_name = msg[msg.index("\"", search_point_begin) + 1:msg.index("\n", search_point_begin) - 1]
                                if routing["process"]["Calculate Route"].has_key("groups"):
                                    if routing["process"]["Calculate Route"]["groups"].has_key(dst_name):
                                        routing["process"]["Calculate Route"]["groups"][dst_name]["total"].append(cur_route_match)
                                    else:
                                        routing["process"]["Calculate Route"]["groups"][dst_name] = {}
                                        routing["process"]["Calculate Route"]["groups"][dst_name]["total"] = []
                                        routing["process"]["Calculate Route"]["groups"][dst_name]["total"].append(cur_route_match)
                                else:
                                    routing["process"]["Calculate Route"]["groups"] = collections.OrderedDict()
                                    routing["process"]["Calculate Route"]["groups"][dst_name] = {}
                                    routing["process"]["Calculate Route"]["groups"][dst_name]["total"] = []
                                    routing["process"]["Calculate Route"]["groups"][dst_name]["total"].append(cur_route_match)
                                
                                if routing["process"].has_key("Calculate Guidance") \
                                and routing["process"]["Calculate Guidance"].has_key("matchs") \
                                and routing["process"]["Calculate Guidance"]["matchs"]:
                                    cal_guidance_matchs = routing["process"]["Calculate Guidance"]["matchs"][:]
                                    if cal_route_index == len(cal_route_matchs) - 1:
                                        for cal_guidance_match in cal_guidance_matchs:
                                            if cal_guidance_match["begin_index"] > cur_route_match["begin_index"]:
                                                if routing["process"]["Calculate Guidance"].has_key("groups"):
                                                    if routing["process"]["Calculate Guidance"]["groups"].has_key(dst_name):
                                                        routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"].append(cal_guidance_match)
                                                    else:
                                                        routing["process"]["Calculate Guidance"]["groups"][dst_name] = {}
                                                        routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"] = []
                                                        routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"].append(cal_guidance_match)
                                                else:
                                                    routing["process"]["Calculate Guidance"]["groups"] = collections.OrderedDict()
                                                    routing["process"]["Calculate Guidance"]["groups"][dst_name] = {}
                                                    routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"] = []
                                                    routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"].append(cal_guidance_match)
                                            
                                    else:
                                        for cal_guidance_match in cal_guidance_matchs:
                                            if cal_guidance_match["begin_index"] > cur_route_match["begin_index"]\
                                                and cal_guidance_match["end_index"] < cal_route_matchs[cal_route_index+1]["end_index"]:
                                                if routing["process"]["Calculate Guidance"].has_key("groups"):
                                                    if routing["process"]["Calculate Guidance"]["groups"].has_key(dst_name):
                                                        routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"].append(cal_guidance_match)
                                                    else:
                                                        routing["process"]["Calculate Guidance"]["groups"][dst_name] = {}
                                                        routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"] = []
                                                        routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"].append(cal_guidance_match)
                                                else:
                                                    routing["process"]["Calculate Guidance"]["groups"] = collections.OrderedDict()
                                                    routing["process"]["Calculate Guidance"]["groups"][dst_name] = {}
                                                    routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"] = []
                                                    routing["process"]["Calculate Guidance"]["groups"][dst_name]["total"].append(cal_guidance_match)
                                                
                            cal_route_index += 1

                    cur_row = routing["cell_point"]["left_up"]["row"] + 1
                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")
                        index += 1
                        merge_cell_start_row = cur_row
                        xlsx_file.writeCell(cur_row, routing["cell_point"]["left_up"]["col"], index)

                        cur_col = routing["cell_point"]["left_up"]["col"]
                        for k_2, v_2 in v_1.items():
                            k_2 = k_2.encode("utf-8")
                            if k_2 == "log point":
                                pass
                                group_col = cur_col + 1
                                avg_col = group_col + 1
                                if work_sheet.cell(routing["cell_point"]["left_up"]["row"], group_col).value == None:
                                    xlsx_file.writeCell(routing["cell_point"]["left_up"]["row"], group_col, "groups")
                                if work_sheet.cell(routing["cell_point"]["left_up"]["row"], avg_col).value == None:
                                    xlsx_file.writeCell(routing["cell_point"]["left_up"]["row"], avg_col, "average time cost")
                                if routing["process"].has_key(k_1) and routing["process"][k_1].has_key("groups")\
                                    and routing["process"][k_1]["groups"]:
                                    for group_name, group_value in routing["process"][k_1]["groups"].items():
                                        xlsx_file.writeCell(cur_row, group_col, group_name)
                                        total = 0
                                        cnt = 0
                                        if len(group_value["total"]) > 1:
                                            for result in group_value["total"]:
                                                total += result["delta_time"].total_seconds()
                                                cnt += 1
                                                xlsx_file.writeCell(routing["cell_point"]["left_up"]["row"], avg_col+cnt, "time cost(ms)Round"+str(cnt))
                                                xlsx_file.writeCell(cur_row, avg_col+cnt, result["delta_time"].total_seconds())
                                            avg = round(total/cnt, 3)
                                            xlsx_file.writeCell(cur_row, avg_col, avg)
                                            if routing["cell_point"]["right_down"]["col"] < avg_col + cnt:
                                                routing["cell_point"]["right_down"]["col"] = avg_col + cnt
                                        elif len(group_value["total"]) == 1:
                                            if work_sheet.cell(routing["cell_point"]["left_up"]["row"], avg_col+1).value == None:
                                                xlsx_file.writeCell(routing["cell_point"]["left_up"]["row"], avg_col+1, "time cost(ms)")
                                            xlsx_file.writeCell(cur_row, avg_col+1, group_value["total"][0]["delta_time"].total_seconds())
                                            if routing["cell_point"]["right_down"]["col"] < avg_col + 1:
                                                routing["cell_point"]["right_down"]["col"] = avg_col + 1
                                        
                                        cur_row += 1
                                    merge_cell_end_row = cur_row
                                    xlsx_file.mergeCell(sheet_name, begin_row=merge_cell_start_row,
                                                                end_row=merge_cell_end_row-1)
                                else:
                                    if routing["cell_point"]["right_down"]["col"] < avg_col:
                                        routing["cell_point"]["right_down"]["col"] = avg_col

                            else:
                                cur_col += 1
                                if work_sheet.cell(routing["cell_point"]["left_up"]["row"], cur_col).value == None:
                                    xlsx_file.writeCell(routing["cell_point"]["left_up"]["row"], cur_col, k_2)
                                xlsx_file.writeCell(cur_row, cur_col, v_2)

                    routing["cell_point"]["right_down"]["row"] = work_sheet.max_row
                    xlsx_file.setCellBorder(sheet_name, routing["cell_point"]["left_up"]["row"],
                                                        routing["cell_point"]["left_up"]["col"],
                                                        routing["cell_point"]["right_down"]["row"],
                                                        routing["cell_point"]["right_down"]["col"],) 

                                                        
                elif k == "Search":
                    search = {}
                    search["cell_point"] = {}
                    search["cell_point"]["left_up"] = {}
                    search["cell_point"]["right_down"] = {}
                    search["cell_point"]["right_down"]["row"] = 1
                    search["cell_point"]["right_down"]["col"] = 1

                    search["process"] = collections.OrderedDict()

                    if work_sheet.max_row == 1:
                        search["cell_point"]["left_up"]["row"] = work_sheet.max_row
                    else:
                        search["cell_point"]["left_up"]["row"] = work_sheet.max_row + 3
                    pass
                    search["cell_point"]["left_up"]["col"] = 1

                    row_offset = 0
                    index = 0
                    xlsx_file.writeCell(search["cell_point"]["left_up"]["row"] , 1, k)  # write cell "search"
                          
                    for k_1, v_1 in v.items():
                        k_1 = k_1.encode("utf-8")
                        if k_1 == "OneBox_TASDK_Cloud" or k_1 == "OneBox_TASDK_OnBoard" \
                            or k_1 == "OneBox_QTARP_Cloud" or k_1 == "OneBox_QTARP_OnBoard":
                            continue
                        
                        cur_col = 1
                        row_offset += 1
                        index += 1
                        xlsx_file.writeCell(search["cell_point"]["left_up"]["row"] + row_offset, 1, index)

                        for k_2, v_2 in v_1.items():
                            k_2 = k_2.encode("utf-8")
                            
                            if k_2 == "process name":
                                pass
                                cur_col += 1
                                if work_sheet.cell(search["cell_point"]["left_up"]["row"], cur_col).value == None:
                                        xlsx_file.writeCell(search["cell_point"]["left_up"]["row"], cur_col, k_2)
                                xlsx_file.writeCell(search["cell_point"]["left_up"]["row"] + row_offset, cur_col, v_2)

                            elif k_2 == "owner":
                                pass
                                cur_col += 1
                                if work_sheet.cell(search["cell_point"]["left_up"]["row"], cur_col).value == None:
                                        xlsx_file.writeCell(search["cell_point"]["left_up"]["row"], cur_col, k_2)
                                xlsx_file.writeCell(search["cell_point"]["left_up"]["row"] + row_offset, cur_col, v_2)

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
                                
                                matchs = []
                                if begin_logs and end_logs:   # get total matchs
                                    index1 = 0
                                    index2 = 0
                                    
                                    while index1 < len(begin_logs) and index2 < len(end_logs):
                                        match = {}
                                        match["begin_index"] = 0
                                        match["end_index"] = 0
                                        match["delta_time"] = None
                                        begin_index = begin_logs[index1]["index"]
                                        end_index = end_logs[index2]["index"]

                                        if begin_index >= end_index:
                                            index2 += 1
                                            continue
                                        else:
                                            if index1 != len(begin_logs) - 1:
                                                next_begin_index = begin_logs[index1 + 1]["index"]
                                                if next_begin_index < end_index:
                                                    index1 += 1
                                                    continue
                                                else:
                                                    match["begin_index"] = begin_logs[index1]["index"]
                                                    match["end_index"] = end_logs[index2]["index"]
                                                    delta_time = end_logs[index2]["time"] - begin_logs[index1]["time"]
                                                    match["delta_time"] = round(delta_time.total_seconds(), 3)      # get match "delta_time"

                                                    matchs.append(match)
                                                    index1 += 1
                                                    index2 += 1
                                            else:
                                                match["begin_index"] = begin_logs[index1]["index"]
                                                match["end_index"] = end_logs[index2]["index"]
                                                delta_time = end_logs[index2]["time"] - begin_logs[index1]["time"]
                                                match["delta_time"] = round(delta_time.total_seconds(), 3)     # get match "delta_time"
                        
                                                matchs.append(match)
                                                break

                                search["process"][k_1] = {}
                                search["process"][k_1]["groups"] = collections.OrderedDict()
                                if k_1 == "Category":
                                    pattern = re.compile(r'"(\d+)"')
                                elif k_1 == "OneBox":
                                    pattern = re.compile(r'"(.+)"')
                                elif k_1 == "Suggestion":
                                    pattern = re.compile(r'"(.+)"')
                                if matchs:
                                    for match in matchs:
                                        group_log = nav_log.getLog(v_1["key_name"]["search_key"].encode("utf-8"), match["begin_index"], match["end_index"] + 1)
                                        if group_log:
                                            search_result = ""
                                            if k_1 == "Category":
                                                search_result = re.search(r'"(\d+)"', group_log["message"])
                                            elif k_1 == "OneBox":
                                                search_result = re.search(r'"(.+)"', group_log["message"])
                                            elif k_1 == "Suggestion":
                                                search_result = re.search(r'"(.+)"', group_log["message"])
                                            if search_result:
                                                if k_1 == "Category":
                                                    group_name = category[search_result.group(1)]
                                                else:
                                                    group_name = search_result.group(1)
                                                if search["process"][k_1]["groups"].has_key(group_name):
                                                    search["process"][k_1]["groups"][group_name]["total"].append(match)
                                                else:
                                                    search["process"][k_1]["groups"][group_name] = collections.OrderedDict()
                                                    search["process"][k_1]["groups"][group_name]["total"] = []
                                                    search["process"][k_1]["groups"][group_name]["total"].append(match)
                                            else:
                                                print("re.search failed")

                        if v.has_key("OneBox_QTARP_Cloud"):
                            if search.has_key("process"):
                                if search["process"].has_key(k_1):
                                    if search["process"][k_1].has_key("groups"):
                                        for group_name, group_value in search["process"][k_1]["groups"].items():
                                            if group_value.has_key("total"):
                                                group_value["OneBox_QTARP_Cloud"] = []
                                                for match in group_value["total"]:
                                                    begin_key = v["OneBox_QTARP_Cloud"]["log point"]["begin"].encode("utf-8")
                                                    end_key = v["OneBox_QTARP_Cloud"]["log point"]["end"].encode("utf-8")

                                                    begin_log = nav_log.getLog(begin_key, match["begin_index"], match["end_index"] + 1)
                                                    if begin_log:
                                                        end_log = nav_log.getLog(end_key, begin_log["index"],)
                                                        if end_log:
                                                            qtarp_cloud_match = {}
                                                            qtarp_cloud_match["delta_time"] = (end_log["time"] - begin_log["time"]).total_seconds()
                                                            qtarp_cloud_match["begin_index"] = begin_log["index"]
                                                            qtarp_cloud_match["end_index"] = end_log["index"]
                                                            group_value["OneBox_QTARP_Cloud"].append(qtarp_cloud_match)

                        if v.has_key("OneBox_QTARP_OnBoard"):
                            if search.has_key("process"):
                                if search["process"].has_key(k_1):
                                    if search["process"][k_1].has_key("groups"):
                                        for group_name, group_value in search["process"][k_1]["groups"].items():
                                            if group_value.has_key("total"):
                                                group_value["OneBox_QTARP_OnBoard"] = []
                                                for match in group_value["total"]:
                                                    begin_key = v["OneBox_QTARP_OnBoard"]["log point"]["begin"].encode("utf-8")
                                                    end_key = v["OneBox_QTARP_OnBoard"]["log point"]["end"].encode("utf-8")

                                                    begin_log = nav_log.getLog(begin_key, match["begin_index"], match["end_index"] + 1)
                                                    if begin_log:
                                                        end_log = nav_log.getLog(end_key, begin_log["index"], match["end_index"])
                                                        if end_log:
                                                            qtarp_onboard_match = {}
                                                            qtarp_onboard_match["delta_time"] = (end_log["time"] - begin_log["time"]).total_seconds()
                                                            qtarp_onboard_match["begin_index"] = begin_log["index"]
                                                            qtarp_onboard_match["end_index"] = end_log["index"]
                                                            group_value["OneBox_QTARP_OnBoard"].append(qtarp_onboard_match)

                        if v.has_key("OneBox_TASDK_Cloud"):
                            begin_key = v["OneBox_TASDK_Cloud"]["log point"]["begin"].encode("utf-8")
                            end_key = v["OneBox_TASDK_Cloud"]["log point"]["end"].encode("utf-8")
                            if search.has_key("process"):
                                if search["process"].has_key(k_1):
                                    if search["process"][k_1].has_key("groups"):
                                        for group_name, group_value in search["process"][k_1]["groups"].items():
                                            if group_value.has_key("total"):
                                                group_value["OneBox_TASDK_Cloud"] = []
                                                for match in group_value["total"]:
                                                    begin_log = nav_log.getLog(begin_key, match["begin_index"], match["end_index"] + 1)
                                                    if begin_log:
                                                        end_log = nav_log.getLog(end_key, begin_log["index"], match["end_index"] + 1)
                                                        if end_log:
                                                            tasdk_cloud_match = {}
                                                            tasdk_cloud_match["delta_time"] = (end_log["time"] - begin_log["time"]).total_seconds()
                                                            tasdk_cloud_match["begin_index"] = begin_log["index"]
                                                            tasdk_cloud_match["end_index"] = end_log["index"]
                                                            group_value["OneBox_TASDK_Cloud"].append(tasdk_cloud_match)

                        if v.has_key("OneBox_TASDK_OnBoard"):
                            if search.has_key("process"):
                                if search["process"].has_key(k_1):
                                    if search["process"][k_1].has_key("groups"):
                                        for group_name, group_value in search["process"][k_1]["groups"].items():
                                            if group_value.has_key("total"):
                                                group_value["OneBox_TASDK_OnBoard"] = []
                                                for match in group_value["total"]:
                                                    begin_key = v["OneBox_TASDK_OnBoard"]["log point"]["begin"].encode("utf-8")
                                                    end_key = v["OneBox_TASDK_OnBoard"]["log point"]["end"].encode("utf-8")

                                                    begin_log = nav_log.getLog(begin_key, match["begin_index"], match["end_index"] + 1)
                                                    if begin_log:
                                                        end_log = nav_log.getLog(end_key, begin_log["index"], match["end_index"] + 1)
                                                        if end_log:
                                                            tasdk_onboard_match = {}
                                                            tasdk_onboard_match["delta_time"] = (end_log["time"] - begin_log["time"]).total_seconds()
                                                            tasdk_onboard_match["begin_index"] = begin_log["index"]
                                                            tasdk_onboard_match["end_index"] = end_log["index"]
                                                            group_value["OneBox_TASDK_OnBoard"].append(tasdk_onboard_match) 

                        # let's fill xlsx
                        if search["process"] and search["process"].has_key(k_1) and search["process"][k_1] \
                                             and search["process"][k_1].has_key("groups") and search["process"][k_1]["groups"]:
                            group_col = cur_col + 1
                            sub_group_col = group_col + 1
                            avg_col = sub_group_col + 1
                            if work_sheet.cell(search["cell_point"]["left_up"]["row"], group_col).value == None:
                                xlsx_file.writeCell(search["cell_point"]["left_up"]["row"], group_col, "group")
                            if work_sheet.cell(search["cell_point"]["left_up"]["row"], sub_group_col).value == None:
                                xlsx_file.writeCell(search["cell_point"]["left_up"]["row"], sub_group_col, "sub group")
                            if work_sheet.cell(search["cell_point"]["left_up"]["row"], avg_col).value == None:
                                xlsx_file.writeCell(search["cell_point"]["left_up"]["row"], avg_col, "average time cost")
                        
                            if search["process"][k_1].has_key("groups") and search["process"][k_1]["groups"]:
                                merge_cell_begin_row = search["cell_point"]["left_up"]["row"] + row_offset
                                for group_name, group_value in search["process"][k_1]["groups"].items():
                                    xlsx_file.writeCell(search["cell_point"]["left_up"]["row"]+row_offset, group_col, str(group_name))
                                    for sub_group_name, sub_group_value in group_value.items():
                                        xlsx_file.writeCell(search["cell_point"]["left_up"]["row"]+row_offset, sub_group_col, str(sub_group_name))

                                        match_cnt = 0
                                        sub_group_total = 0
                                        sub_group_avg = 0
                                        if sub_group_value:
                                            if len(sub_group_value) > 1:
                                                for match in sub_group_value:
                                                    pass
                                                    match_cnt += 1
                                                    sub_group_total += match["delta_time"]
                                                    if work_sheet.cell(search["cell_point"]["left_up"]["row"], avg_col + match_cnt).value == None:
                                                        xlsx_file.writeCell(search["cell_point"]["left_up"]["row"], avg_col + match_cnt, "time cost(ms)Round" + str(match_cnt))
                                                    xlsx_file.writeCell(search["cell_point"]["left_up"]["row"]+row_offset, avg_col + match_cnt, match["delta_time"])
                                                sub_group_avg = round(sub_group_total/match_cnt, 3)
                                                xlsx_file.writeCell(search["cell_point"]["left_up"]["row"] + row_offset, avg_col, sub_group_avg)

                                                if search["cell_point"]["right_down"]["col"] < avg_col + match_cnt:
                                                    search["cell_point"]["right_down"]["col"] = avg_col + match_cnt
                                            else:
                                                pass
                                                if work_sheet.cell(search["cell_point"]["left_up"]["row"], avg_col + 1).value == None:
                                                        xlsx_file.writeCell(search["cell_point"]["left_up"]["row"], avg_col + 1, "time cost(ms)Round")
                                                xlsx_file.writeCell(search["cell_point"]["left_up"]["row"]+row_offset, avg_col + 1, sub_group_value[0]["delta_time"])

                                                if search["cell_point"]["right_down"]["col"] < avg_col + 1:
                                                    search["cell_point"]["right_down"]["col"] = avg_col + 1
                                        row_offset += 1 
                                row_offset -= 1
                                merge_cell_end_row = search["cell_point"]["left_up"]["row"] + row_offset
                                xlsx_file.mergeCell(sheet_name, begin_row=merge_cell_begin_row, end_col=4,
                                                end_row=merge_cell_end_row)
                        else:
                            if search["cell_point"]["right_down"]["col"] < cur_col:
                                search["cell_point"]["right_down"]["col"] = cur_col

                    search["cell_point"]["right_down"]["row"] = work_sheet.max_row

                    xlsx_file.setCellBorder(sheet_name, search["cell_point"]["left_up"]["row"],
                                                        search["cell_point"]["left_up"]["col"],
                                                        search["cell_point"]["right_down"]["row"],
                                                        search["cell_point"]["right_down"]["col"],)

                elif k == "MapDisplay":
                    pass
                    mapdisplay = {}
                    mapdisplay["cell_point"]={}
                    mapdisplay["cell_point"]["left_up"]={}
                    mapdisplay["cell_point"]["right_down"]={}
                    mapdisplay["cell_point"]["right_down"]["row"] = 1
                    mapdisplay["cell_point"]["right_down"]["col"] = 1

                    mapdisplay["object"] = collections.OrderedDict()
                    
                    if work_sheet.max_row == 1:
                        mapdisplay["cell_point"]["left_up"]["row"] = work_sheet.max_row
                    else:
                        mapdisplay["cell_point"]["left_up"]["row"] = work_sheet.max_row + 3
                    mapdisplay["cell_point"]["left_up"]["col"] = 1

                    xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"], 1, k)

                    row_offset = 0
                    index = 0
                    for k_1, v_1 in v.items():
                        mapdisplay["object"][k_1] = {}

                        k_1 = k_1.encode("utf-8")

                        cur_col = 1
                        row_offset += 1
                        index += 1
                        xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"] + row_offset, 1, index)

                        for k_2, v_2 in v_1.items():
                            cur_col += 1
                            k_2 = k_2.encode("utf-8")
                            if k_2 == "process name":
                                if work_sheet.cell(mapdisplay["cell_point"]["left_up"]["row"], cur_col).value == None:
                                    xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"], cur_col, k_2)

                                xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"] + row_offset, cur_col, v_2)

                            elif k_2 == "owner":
                                if work_sheet.cell(mapdisplay["cell_point"]["left_up"]["row"], cur_col).value == None:
                                    xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"], cur_col, k_2)

                                xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"] + row_offset, cur_col, v_2)
                            if k_2 == "log point":
                                mapdisplay["object"][k_1]["group"] = collections.OrderedDict()
                                mapdisplay["object"][k_1]["total"] = {}
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
                                    mapdisplay["object"][k_1]["total"]["matchs"] = []
                                    index1 = 0
                                    index2 = 0
                                    
                                    while index1 < len(begin_logs) and index2 < len(end_logs):
                                        match = {}
                                        match["begin_index"] = 0
                                        match["end_index"] = 0
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
                                                match["begin_index"] = begin_logs[index1]["index"]
                                                match["end_index"] = end_logs[index2]["index"]
                                                match["index"] = begin_logs[index1]["index"]          # get match "index"
                                                delta_time = end_logs[index2]["time"] - begin_logs[index1]["time"]
                                                match["delta_time"] = round(delta_time.total_seconds(), 3)     # get match "delta_time"
                        
                                                mapdisplay["object"][k_1]["total"]["matchs"].append(match)
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

                                                mapdisplay["object"][k_1]["total"]["matchs"].append(match)
                                                index1 += 1
                                                index2 += 2

                                for k, v in mapdisplay["object"][k_1]["group"].items():
                                    if v:
                                        match_cnt = 0
                                        delta_total = 0
                                        for match in v["matchs"]:
                                            delta_total += match["delta_time"]
                                            match_cnt += 1
                                        if match_cnt != 0:
                                            v["avg"] = round(delta_total / match_cnt, 3)
                                        else:
                                            v["avg"] = None

                                if mapdisplay["object"][k_1]["group"]:
                                    if work_sheet.cell(mapdisplay["cell_point"]["left_up"]["row"], cur_col).value == None:
                                        xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"], cur_col, "average time comst(ms)")
                                
                                    for k, v in mapdisplay["object"][k_1]["group"].items():
                                        if v:
                                            xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"] + row_offset, cur_col, v["avg"])

                                            match_offset = 0
                                            for match in v["matchs"]:
                                                match_offset += 1
                                                if work_sheet.cell(mapdisplay["cell_point"]["left_up"]["row"] + row_offset, cur_col + match_offset).value == None:
                                                    xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"], cur_col + match_offset, "time cost(ms)Round" + str(match_offset))
                                                xlsx_file.writeCell(mapdisplay["cell_point"]["left_up"]["row"] + row_offset, cur_col + match_offset, match["delta_time"])
                                            if mapdisplay["cell_point"]["right_down"]["col"] < cur_col + match_offset:
                                                mapdisplay["cell_point"]["right_down"]["col"] = cur_col + match_offset
                                else:
                                    if mapdisplay["cell_point"]["right_down"]["col"] < cur_col - 1:
                                        mapdisplay["cell_point"]["right_down"]["col"] = cur_col - 1

                    mapdisplay["cell_point"]["right_down"]["row"] = work_sheet.max_row
                    xlsx_file.mergeCell(sheet_name, begin_row=mapdisplay["cell_point"]["left_up"]["row"],
                                                    end_row=mapdisplay["cell_point"]["right_down"]["row"])
                    
                    xlsx_file.setCellBorder(sheet_name, mapdisplay["cell_point"]["left_up"]["row"],
                                                        mapdisplay["cell_point"]["left_up"]["col"],
                                                        mapdisplay["cell_point"]["right_down"]["row"],
                                                        mapdisplay["cell_point"]["right_down"]["col"],)                                       
        
            xlsx_file.resize(sheet_name)
    xlsx_file.create(xlsx_file_path)

