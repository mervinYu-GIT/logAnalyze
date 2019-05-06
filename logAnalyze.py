#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
from argparse import ArgumentParser

from navXlsx import NavXlsxFile


class NavLogAnalyze:
    pass


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument('log_file', help = "input log file")
    arg_parser.add_argument('--cfg', help="config file, eg: path/config.json")
    arg_parser.add_argument('--xlsx', help='xlsx file')
    args = arg_parser.parse_args()

    if args.log_file:
        log_file = args.log_file
    if args.cfg:
        cfg_file = args.cfg
    else:
        cfg_file = './config.json'

    if args.xlsx:
        xlsx_file = args.xlsx
    else:
        xlsx_file = './navLog.xlsx'

    xlsx_file = NavXlsxFile(xlsx_file, cfg_file, log_file)
    xlsx_file.load_data('navLog')
    xlsx_file.resize()
    xlsx_file.create()
    
