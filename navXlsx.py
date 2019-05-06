#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import json

import openpyxl
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment

from navLog import NavLogFile
from public_fun import calcTime

class NavXlsxFile:
    """ navigation xlsx file """
    def __init__(self, xlsx_file, cfg_file, log_file):
        self.cfg_file = cfg_file
        self.xlsx_file = xlsx_file
        self.log_file = NavLogFile(log_file)
        pass


    def load_data(self, sheet_name, row=1, col=1):
        try:
            self.work_book = Workbook()
        except:
            open('xlsx file open faild!')
            sys.exit()

        row += 1
        work_sheet = self.work_book.create_sheet(sheet_name, 0)
        self.current_sheet = work_sheet
        with open(self.cfg_file, 'r') as json_f:
            try:
                json_cfg = json.load(json_f)
            except:
                print(self.cfg_file + ' is not json fromat')
                sys.exit()

            for k, v in json_cfg.items():
                work_sheet.cell(row, col, k).alignment = \
                    Alignment(horizontal = 'center', vertical = 'center')
                for k_1, v_1 in v.items():
                    col += 1
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
                                beginTime = self.log_file.begin_time
                            else:
                                beginTime = self.log_file.searchTime(v_2['begin'], 'Message')
                                if beginTime == -1:
                                    beginTime = self.log_file.begin_time
                                    print('start point not found! begin time was seted to log begin time.')

                            if v_2['end'] == '':
                                endTime = self.log_file.end_time
                            else:
                                endTime = self.log_file.searchTime(v_2['end'], 'Message')
                                if endTime == -1:
                                    endTime = self.log_file.end_time
                                    print('end point not found! end time was seted to log end time.')

                            delta_time = calcTime(beginTime, endTime)
                            work_sheet.cell(row, col, str(delta_time)).alignment = \
                                Alignment(horizontal = 'center', vertical = 'center')        # for openpyxl
                            try:
                                work_sheet.cell(1, col, 'time comsuming').alignment = \
                                    Alignment(horizontal = 'center', vertical = 'center')     # for openpyxl
                            except:
                                pass

                        else:   # <if k_2 == 'log point'>
                            work_sheet.cell(row, col, v_2).alignment = \
                                Alignment(horizontal = 'center', vertical = 'center')      # for openpyxl
                            try:
                                work_sheet.cell(1, col, k_2).alignment = \
                                    Alignment(horizontal = 'center', vertical = 'center')    # for openpyxl
                            except:
                                pass
                    row += 1
                    col -= (len(v_1) + 1)
                row += 1
                col -= (len(v) - 2)


    def resize(self):
        for col in range(self.current_sheet.max_column):
            col_width = 0
            for row in range(self.current_sheet.max_row):
                cell_value = self.current_sheet.cell(row+1, col+1).value
                if len(str(cell_value)) > col_width:
                    col_width = len(str(cell_value))

            self.current_sheet.column_dimensions[get_column_letter(col+1)].width\
                = float(col_width + 3.0)

    def create(self):
        try:
            self.work_book.save(self.xlsx_file)
        except:
            print('create xlsx file faild!')
            sys.exit()
