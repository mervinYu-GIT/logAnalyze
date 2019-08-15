# Navigation log analyze

## Depend on

1. python 2.7.15
2. openpyxl module
3. collections module

## Synopsis

python.exe logAnalyze.py navlog_file1 [navlog_file2 [navlog_file3] ...] [--cfg config_file] [--xlsx xlsx_file]

## Description

This python script use '.json' configured file to create '.xlsx ' file.

navlog_file: This paramet must be needed in cmd line, it is that you want to analyze. if you want to use multiplt log files, just type 'python.exe logAnalyze.py navlog_file1 navlog_file2 ... ' in windows prompt or shell

--cfg config_file: optional parameters, specify the json file that you want to use. default './config.json'

--xlsx xlsx_file: optional parameters, specify the excle file that you want to save. default './navLog.xlsx'

## How to

### install openpyxl

1. open prompt/shell
2. type "pip install openpyxl"
3. exec python interpreter : python.exe
4. type "import openpyxl", if nothing return, congratulation, you have done!

### use

1. Open prompt/shell in windows or linux
2. Change the work path to loganalyze/
3. Rewrite a configuration file that meets your requirements according to the config.json_template file format. Confirm the file path, eg: ./my_config.json
4. Identify the path to the navigation log file that you need to analyze，eg: ./navigation.log
5. Make sure you want to save the path to the excle file, eg: ./log_excle/navLog.xlsx, the ./log_excle must be exist.
6. then type "python.exe logAnalyze.py ./navigation.log --cfg ./my_config.json --xlsx ./log_excle/navLog.xlsx"
7. if you want to batch processing .log file under the same folder, just tap folder path. like this : python logAnalyze.py log_folder/ ...
