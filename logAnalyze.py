#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from os import path
from argparse import ArgumentParser
from navXlsx import NavXlsxFile
from navLog import NavLogFile


class NavLogAnalyze:
    pass


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument('log_files', nargs = '*', help = "input log file")
    arg_parser.add_argument('--cfg', help="config file, eg: path/config.json")
    arg_parser.add_argument('--xlsx', help='xlsx file')
    args = arg_parser.parse_args()

    if args.log_files:
        log_files = args.log_files
    if args.cfg:
        cfg_file = args.cfg
    else:
        cfg_file = './config.json'

    if args.xlsx:
        xlsx_file = args.xlsx
    else:
        xlsx_file = './navLog.xlsx'

    xlsx_file = NavXlsxFile(xlsx_file, cfg_file)
    for log_file in log_files:
        nav_log_file = NavLogFile(log_file)
        xlsx_file.load_data(nav_log_file, path.basename(log_file).split('.')[0])
        xlsx_file.resize()
    xlsx_file.create()
    
