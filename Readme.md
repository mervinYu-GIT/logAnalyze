# Log analyze

## Description

读取navigationlog文件，将文件内容转换成列表或字典的形式，根据配置条件输出相应内容。输出可以是终端也可以是文件。

## log文件的数据格式

Log Level|Time|PID|Category|File|Function(Line)|Message

1. log文件内容按照以上顺序排列，大部分log内容以行的形式保存。
2. 在有systemSetting, calculateRoute 和 RouteComputationWork时，Message信息以多行存储并且以单独的换行符结束。

### 组织文件信息

1. 将文件内容组织为字典列表的形式。
2. 将字典列表的内容组织为字典嵌套字典的形式。
3. 设计命令行格式以及相关参数。

### json文件操作

#### json 格式

<https://json.org/>
config.json

#### python 操作json文件模块

#### execl 文件操作

[xlwt操作excel](https://www.jianshu.com/p/4e39444d5ebc)

1. xlwt, wlrd 模块的使用
2. 创建工作簿
3. 创建工作表
4. 录入信息

## 可配置的信息提取规则

## 展示信息

### 以TXT文件的形式

### 以excel文件的数据形式

## Function descriptino

### 1. class navLog

* file_path: log文件路径

#### class method

##### navLog.__init__(self, navLogFile)

解析loge文件，以程序可识别的数据结构保存log文件的信息

##### navLog.itemParsing(self, item)

根据item指定的列对log信息进行分类，结果存储在字典中，
字典格式{item:{count:val, list:[]}, ...}
item.count 记录log文件中相同item的log数量，item.list保存这些log。

* item:
  格式：字符串格式
  取值范围：['Log Level', 'Time', 'PID', 'Category', 'File', 'Function(Line)', 'Message']

* itemDict:
  * 格式： {'count' : val, 'list' : []}
    * itemDict.count:
      * 格式：val
      * 记录相同类型的item出现的次数
    * itemDict.list:
      * 类型：list
      * 储存相同item类型的log

* logItemDict:  作为结果进行返回
  * 格式：{item:itemDict, ...}

##### navLog.beginTime(self)

以python datetime时间格式返回log开始时间。

##### navLog.endTime(self)

以python datetime时间格式返回log结束时间。

##### navLog.search(self, key, item, star, end)

在logList查找指定项中的key,如果key存在，则返回查找到的log.

* key:
  * 类型：str
  * 需要查找的关键字
* item:
  * 类型：str
  * 指定查找的log项
  * 取值范围：logHeadRow
* start，end:
  * 类型：int
  * 指定查找的范围。默认start=0, end=-1
* 返回值：
  * 匹配的log
  * -1: 未找到匹配的log

#### function calcTime(beginTime, endTime)

用timedelta的形式返回endTime与beginTime之间的时间间隔。
  
## Bug List

1. UnboundLocalError: local variable 'fd' referenced before assignment
2. Permission denied: './navLog.xls'
文件被打开，关闭文件。
