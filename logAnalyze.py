#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from os import path
import json
import re  
from datetime import datetime
from argparse import ArgumentParser
import collections
from navXlsx import NavXlsxFile
from navLog import NavLogFile


def calcTime(beginTime, endTime):
    """ calc deltatime """
    try:
        delta_time = endTime - beginTime
        return delta_time
    except:
        print('endTime must bigger than beginTime.')


def getFileList( p ):
        p = str( p )
        if p=="":
              return [ ]
        p = p.replace( "/","\\")
        if p[ -1] != "\\":
             p = p+"\\"
        a = os.listdir( p )
        b = [ x   for x in a if os.path.isfile( p + x ) ]
        return b


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
    print (log_files)

    if args.cfg:
        cfg_file = args.cfg
    else:
        cfg_file = './config.json'

    if args.xlsx:
        xlsx_file_path = args.xlsx
    else:
        xlsx_file_path = './navLog.xlsx'

    xlsx_file = NavXlsxFile()
    with open(cfg_file, 'r') as json_file:
        try:
            json_data = json.load(json_file, object_pairs_hook=collections.OrderedDict)
        except:
            print(cfg_file + ' is not json format!')
            sys.exit()

        for log_file in log_files:
            nav_log_file = NavLogFile(log_file)
            sheet_name = path.basename(log_file).split('.')[0]
            xlsx_file.create_sheet(sheet_name)
            work_sheet = xlsx_file.select_sheet(sheet_name)
            
            origin_point = {'row':1, 'col':1}
            route_cursor = {}
            search_cursor = {}
            route_flag = 0
            search_flag = 0

            # sheet_data attribute
            sheet_data_attr = {}

            for k, v in json_data.items():
                row_offset = 0
                col_offset = 0 
                
                # set list default
                first_key = k.encode('utf-8')
                sheet_data_attr.setdefault(first_key, {})
                sheet_data_attr[first_key].setdefault('max_col', 0)
                sheet_data_attr[first_key].setdefault('data_cnts', [])
                sheet_data_attr[first_key].setdefault('total_times', [])
                sheet_data_attr[first_key].setdefault('avg_times', [])
                sheet_data_attr[first_key].setdefault('origin_point', {})
                sheet_data_attr[first_key]["origin_point"]['col'] = origin_point['col']
                sheet_data_attr[first_key]["origin_point"]['row'] = origin_point['row']
                
                xlsx_file.write_cell(origin_point['row'] ,origin_point['col'], k)
                col_offset += 1
                row_offset += 1
                index = 1

                for k_1, v_1 in v.items():
                    xlsx_file.write_cell(origin_point['row'] + row_offset,\
                        origin_point['col'] - 1 + col_offset, index)
                    index += 1
                    for k_2, v_2 in v_1.items():
                        beginTimes = []
                        endTimes = []
                        delta_times = []

                        if k_2 == 'log point':

                            if v_2['begin'] == '':        # search begin time in file logs
                                beginTimes = beginTimes.append(nav_log_file.beginTime())
                            else:
                                begin_logs = nav_log_file.searchLog(v_2['begin'], "Message")
                                if begin_logs:
                                    begin_times = nav_log_file.getLogsTime(begin_logs)
                                    begin_times.sort()
                                else:
                                    print(str(v_2['begin']) + ' is not found!')
                                    break
                            
                            if v_2['end'] == '':        # search begin time in file logs
                                endTimes = endTimes.append(nav_log_file.endTime())
                            else:
                                end_logs = nav_log_file.searchLog(v_2['end'], "Message")
                                if end_logs:
                                    end_times = nav_log_file.getLogsTime(end_logs)
                                    end_times.sort()
                                else:
                                    print(str(v_2['end']) + ' is not found!')
                                    break

                            delta_times = nav_log_file.getDeltaTime(begin_times, end_times)
                            
                            round_index = 0
                            total_time = 0
                            for delta_time in delta_times:
                                round_index += 1
                                total_time = total_time + delta_time.total_seconds()
                                
                                if len(delta_times) > 1:
                                    # round_index += 1
                                    if work_sheet.cell(origin_point['row'], origin_point['col'] + col_offset).value == None:
                                        xlsx_file.write_cell(origin_point['row'],\
                                            origin_point['col'] + col_offset, "time cost(s)Round" + str(round_index))
                                else:
                                    if work_sheet.cell(origin_point['row'], origin_point['col'] + col_offset).value == None:
                                        xlsx_file.write_cell(origin_point['row'],\
                                            origin_point['col'] + col_offset, "time cost(s)Round")

                                xlsx_file.write_cell(origin_point['row'] + row_offset,\
                                    origin_point['col'] + col_offset, delta_time.total_seconds())
                                col_offset += 1

                            #save data count
                            sheet_data_attr[first_key]["data_cnts"].append(round_index)
                            # save total time
                            sheet_data_attr[first_key]["total_times"].append(total_time)
                            # save average time
                            sheet_data_attr[first_key]["avg_times"].append(round(total_time/round_index, 3))

                        else:   # <if k_2 == 'log point'>
                            xlsx_file.write_cell(origin_point['row'] + row_offset,\
                                origin_point['col'] + col_offset, v_2)
                                    
                            if work_sheet.cell(origin_point['row'], origin_point['col'] + col_offset).value == None:
                                xlsx_file.write_cell(origin_point['row'],\
                                    origin_point['col'] + col_offset, k_2)  
                            col_offset += 1

                        # get max col
                        if origin_point['col'] + col_offset > sheet_data_attr[first_key]['max_col']:
                            sheet_data_attr[first_key]['max_col'] = origin_point['col'] + col_offset

                    row_offset += 1
                    col_offset -= (len(v_1) + len(delta_times) - 1)
                origin_point['row'] = work_sheet.max_row + 3

            # add average and total colum
            for k, v in sheet_data_attr.items():
                index = 0
                while index < len(v['data_cnts']):
                    data_cnt = v['data_cnts'][index]
                    if data_cnt > 1:
                        if work_sheet.cell(origin_point['row'], origin_point['col'] + col_offset).value == None:
                            xlsx_file.write_cell(v['origin_point']['row'], v['max_col'],\
                                'total_times')
                        xlsx_file.write_cell(v['origin_point']['row'] + index + 1, v['max_col'],\
                             v['total_times'][index])

                        if work_sheet.cell(origin_point['row'], origin_point['col'] + col_offset).value == None:
                            xlsx_file.write_cell(v['origin_point']['row'], v['max_col'] + 1,\
                                'agv_times')
                        xlsx_file.write_cell(v['origin_point']['row'] + index + 1, v['max_col'] + 1,\
                            v['avg_times'][index])
                        
                    index += 1




            xlsx_file.resize(sheet_name)
    xlsx_file.create(xlsx_file_path)



# sheet_data_attr = {
#     "item":{
#         "origin_point" : {
#             "row" : 0,
#             "col" : 0
#         },
#         "max_col" : 0,
#         "data_cnt" : 0,
#         "totals" : [],
#         "avgs" : []
#     }
# }