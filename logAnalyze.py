#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import json
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment
from datetime import datetime
from argparse import ArgumentParser

from navLog import NavLogFile

# import xlwt   # need installed : pip install xlwt

class NavLogAnalyze:
    pass


def calcTime(beginTime, endTime):
    """ 计算beginTime与endTime之间的时间间隔，以deltatime的格式返回 """
    try:
        delta_time = endTime - beginTime
        return delta_time
    except:
        print('endTime must bigger than beginTime.')


def outPut(fileName, path='./log_xls'):
    if not os.path.exists('path'):
        os.mkdir('./log_xls')

    work_book.save(path + fileName)






if __name__ == "__main__":

    # logAnalyze = LogAnalyze()
    # logAnalyze.runWork()

    arg_parser = ArgumentParser()
    arg_parser.add_argument('inputFile', help = "input log file")
    arg_parser.add_argument('--cfg', help="config file, eg: path/config.json")
    args = arg_parser.parse_args()

    if args.inputFile:
      nav_log1 = NavLogFile(args.inputFile)
    if args.cfg:
        config_file = args.cfg
    print('------------------------------------------------------------')

    # 创建excel文件
    # work_book = xlwt.Workbook('utf-8')  # 工作簿
    # work_sheet = work_book.add_sheet('navLog')
    # work_sheet.write(1, 0, 'this is test')

    work_book = Workbook()
    work_sheet = work_book.active
    work_sheet.title = 'navLog'

    # print(args)
    row = 2
    col = 1
    with open(config_file, 'r') as json_f:
        json_cfg = json.load(json_f)
        print(json_cfg)
        for k, v in json_cfg.items():
            # work_sheet.write(row, col, k)    # for xlwt
            work_sheet.cell(row, col, k).alignment = \
                Alignment(horizontal = 'center', vertical = 'center')
            for k_1, v_1 in v.items():
                col += 1
                # work_sheet.write(row, col, k_1)  # for xlwt
                work_sheet.cell(row, col, k_1).alignment = \
                    Alignment(horizontal = 'center', vertical = 'center')     # for openpyxl
                for k_2, v_2 in v_1.items():
                    col += 1
                    if k_2 == 'log point':
                        """
                            1. 查找log
                            2. 求出deltatime
                            3. 转换deltatime
                            4. 写入work_sheet
                        """
                        if v_2['begin'] == '':
                            beginTime = nav_log1.begin_time
                        else:
                            beginTime = nav_log1.searchTime(v_2['begin'], 'Message')
                            if beginTime == -1:
                                beginTime = nav_log1.begin_time
                                print('start point not found! begin time was seted to log begin time.')

                        if v_2['end'] == '':
                            endTime = nav_log1.end_time
                        else:
                            endTime = nav_log1.searchTime(v_2['end'], 'Message')
                            if endTime == -1:
                                endTime = nav_log1.end_time
                                print('end point not found! end time was seted to log end time.')

                        delta_time = calcTime(beginTime, endTime)
                        # work_sheet.write(row, col, str(delta_time))     # for xlwt
                        work_sheet.cell(row, col, str(delta_time)).alignment = \
                            Alignment(horizontal = 'center', vertical = 'center')        # for openpyxl
                        # work_sheet.cell(row, col).alignment = Alignment(horizontal='center', vertical = 'center')
                        try:
                            # work_sheet.write(0, col, 'time comsuming')  # for xlwt
                            work_sheet.cell(1, col, 'time comsuming').alignment = \
                                Alignment(horizontal = 'center', vertical = 'center')     # for openpyxl
                        except:
                            pass

                    else:   # <if k_2 == 'log point'>
                        # work_sheet.write(row, col, v_2)   # for xlwt
                        work_sheet.cell(row, col, v_2).alignment = \
                            Alignment(horizontal = 'center', vertical = 'center')      # for openpyxl
                        try:
                            # work_sheet.write(0, col, k_2) # for xlwt
                            work_sheet.cell(1, col, k_2).alignment = \
                                Alignment(horizontal = 'center', vertical = 'center')    # for openpyxl
                        except:
                            pass
                row += 1
                col -= (len(v_1) + 1)
            row += 1
            col -= (len(v) - 2)

    # 调整单元格大小
    # work_sheet.column_dimensions['A'].width = 20.0
    # work_sheet.row_dimensions[1].height = 80
    print(work_sheet.max_column)
    print(work_sheet.max_row)
    for col_temp in range(work_sheet.max_column):
        col_width = 0
        cell_value = None
        for row_temp in range(work_sheet.max_row):
            cell_value = work_sheet.cell(row_temp+1, col_temp+1).value
            print(cell_value)
            if len(str(cell_value)) > col_width:
                col_width = len(str(cell_value))
        print(col_width)
        print('------------------------------------------------')
        work_sheet.column_dimensions[get_column_letter(col_temp+1)].width = float(col_width + 3.0)

    work_book.save('./navLog.xlsx')                # for xlwt and openpyxl

