#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
"""
INI 格式文件解析器
"""

version = "0.0.1"
version_info = (0, 0, 1)


class INIParse(dict):

    def __init__(self):
        """
        返回一个 INIParse 对象，后续的一些操作都是基于这个对象进行的。
        如果要做修改。可以在实例化INIParse对象之后来修改默认的各种分隔符，这些分隔符在属性里面。
        """
        self.comment_symbol = [";"] # 注释识别符，可以支持多个
        self.section_symbol = ("[", "]") # 分组识别标识，第一项是开头，第二项是结尾
        self.string_symbol = ("\"", "'") # 字符串识别符号。
        self.true_boolean_symbol = ("true",) # bool 类型里面 True 的关键字
        self.false_boolean_symbol = ("false",) # bool 类型里面 False 的关键字
        self.none_boolean_symbol = ("null", "none") # 表示 None 类型的关键字
        self.list_symbol = "[]" # key 后面用来表示这个是list 的表示
        self.include_symbol = "@include " # include 操作识别
        self.delimiters = ("=", ":") # key-value 分隔符
        self.section_delimiters = "." # 分组里面表示层级关系的符号
        self.file_list = []
        self.read_file_list = []
        self.read_file_encoding = None
        self._cursor = {} # 游标

    def __getattr__(self, name):
        """
        支持对象方式获取属性
        """
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def read(self, filenames, encoding=None):
        """
        读取配置文件，可以传入一个数组，支持多个配置文件解析
        """
        self.read_file_encoding = encoding
        if isinstance(filenames, str):
            filenames = [filenames]
        for filename in filenames:
            try:
                with open(filename, encoding=encoding) as fp:
                    self._read(fp, filename)
            except OSError:
                continue
            if filename not in self.read_file_list:
                self.read_file_list.append(filename)
        return self.read_file_list

    def read_file(self, f, source=None):
        """
        读取配置文件，只支持一个，参数是文件句柄
        """
        if source is None:
            try:
                source = f.name
                self.read_file_list.append(source)
            except AttributeError:
                source = '<???>'
        self._read(f, source)

    def read_string(self, string, source='<string>'):
        """
        从字符串中读取配置文件。
        """
        sfile = io.StringIO(string)
        self._read(sfile, source)

    def read_dict(self, dictionary):
        """
        从字典里面加载进配置文件里面。可以用于字典格式转换配置文件格式
        """
        self.update(dictionary)

    def _read(self, fp, fpname):
        """
        读取和解析每一行内容
        """
        self.file_list.append(fpname)
        for line in fp:
            line = line.strip()
            if len(line) < 1 or line[0] in self.comment_symbol:
                continue
            if line.lower().startswith(self.include_symbol):
                self._parse_include(line, fp)
                continue
            if all(symbol in self.section_symbol for symbol in
                   [line[0:1], line[-1:]]) and line[0:1] != line[-1:]:
                self._parse_section(line)
                continue
            if any(symbol in line for symbol in self.delimiters):
                self._parse_expression(line)
        fp.close()

    def _parse_include(self, line, fp):
        """
        处理 include 操作，支持相对路径和绝对路径
        """
        filename = line[len(self.include_symbol):]
        filename = filename.strip().strip("\"")
        if not os.path.isabs(filename):
            dir_path = os.path.dirname(fp.name)
            filename = os.path.join(dir_path, filename)
            try:
                with open(filename, encoding=fp.encoding) as new_fp:
                    self._read(new_fp, filename)
            except OSError:
                print("error")
                return

    def _parse_section(self, line):
        """
        解析分组，支持无限极的嵌套即可以有很多个 . 表示层级 [test.test.test.......]
        """
        line = line.strip("[").strip("]") + "."
        self._cursor = self
        while self.section_delimiters in line:
            index = line.index(self.section_delimiters)
            group = line[0:index]
            line = line[index + 1:]
            if group not in self._cursor:
                self._cursor[group] = INIParse()
            self._cursor = self._cursor[group]

    def _parse_expression(self, line):
        """
        解析每个表达式，这里会尝试进行类型转换
        """
        line = line.strip()
        for delimiter in self.delimiters:
            index = line.find(delimiter)
            if index > -1:
                break
        key = line[0:index]
        key = key.strip()
        value = line[index + 1:]
        value = value.strip()
        if value.count("%") >= 2:
            sindex = value.find("%")
            eindex = value.find("%", index + 1)
            variable = value[sindex + 1:eindex]
            if self._check_variable(variable):
                variable = str(self._get_variable(variable))
                value = value[0:sindex] + variable + value[eindex + 1:]
        # 被引号包围的不做类型转换
        if all(symbol in self.string_symbol for symbol in
               (value[0:1], value[-1:])) and value[0:1] is value[-1:]:
            value = value[1:-1]
        else:
            if value.lower() in self.true_boolean_symbol:
                value = True
            elif value.lower() in self.false_boolean_symbol:
                value = False
            elif value.lower() in self.none_boolean_symbol:
                value = None
            elif value.isnumeric():
                value = int(value)
            else:
                try:
                    # 最后尝试做 float 转换
                    value = float(value)
                except ValueError:
                    pass
        # 赋值
        if key.endswith(self.list_symbol):
            key = key.strip(self.list_symbol)
            print(key)
            if key in self._cursor:
                self._cursor[key].append(value)
            else:
                self._cursor[key] = [value]
        else:
            self._cursor[key] = value

    def _check_variable(self, variable, return_bool=True):
        """
        处理层级嵌套的时候检查是否已经存在
        """
        return_value = {"variable": None, "section": None}
        temp_cursor = self
        if self.section_delimiters in variable:
            pass
        else:
            temp_cursor = self._cursor

        while self.section_delimiters in variable:
            index = variable.index(self.section_delimiters)
            key = variable[0:index]
            variable = variable[index + 1:]
            if key in temp_cursor:
                temp_cursor = temp_cursor[key]
            else:
                return False if return_bool else return_value
        if variable in temp_cursor:
            return_value["variable"] = variable
            return_value["section"] = temp_cursor
            return True if return_bool else return_value
        else:
            return False if return_bool else return_value

    def _get_variable(self, variable):
        """
        获取已经存在的分组的游标
        """
        result = self._check_variable(variable, False)
        if result["section"] is None:
            print("Error")
        else:
            return result["section"][result["variable"]]

    def refresh(self):
        """
        刷新操作，会重新需从文件里面加载配置项。字符串和字典方式不支持刷新
        """
        self.clear()
        self.read(self.read_file_list)

    def sections(self):
        """
        返回当前有多少个子项的key
        """
        return self.keys()

    def get_section(self, section):
        """
        获取子项的内容
        """
        if section in self:
            return self[section]
        else:
            return None

    def set_sections(self, section, dictionary):
        """
        修改子项的内容
        """
        if section in self:
            self[section].update(dictionary)
        else:
            self[section] = dictionary

    def get_int(self, key):
        """
        获取一个值，在这里尝试做int转换
        """
        if self.has(key):
            return int(self[key])
        else:
            return False

    def get_float(self, key):
        """
        获取一个值，在这里尝试做float转换
        """
        if self.has(key):
            return float(self[key])
        else:
            return False

    def get_bool(self, key):
        """
        获取一个值，在这里尝试做bool转换
        """
        if self.has(key):
            if str(self[key]).lower() in self.true_boolean_symbol:
                return True
            elif str(self[key]).lower() in self.false_boolean_symbol:
                return False
            else:
                return True
        else:
            return False

    def get_string(self, key):
        """
        获取一个字符串值
        """
        if self.has(key):
            return str(self[key])
        else:
            return False

    def is_none(self, key):
        """
        判断是否是None类型
        """
        if self.has(key) and self[key] is None:
            return True
        else:
            return False

    def has(self, key):
        """
        检查是否包含子项
        """
        return True if key in self else False

    def write_file(self, f):
        """
        写入配置文件，会把自己转换成ini格式写入到文件。参数为文件句柄
        """
        string = self.stringify()
        return f.write(string)

    def stringify(self):
        """
        把配置项转换为ini格式的字符串，方便保存到其他地方，如数据库等。
        """
        return self._section_stringify(self)

    def _section_stringify(self, section, prefix=""):
        """
        对每个分组进行转换城字符串操作。
        """
        string = ""
        for (key, val) in section.items():
            if isinstance(val, INIParse):
                key = (prefix + "." + key).strip(".")
                if not all(isinstance(tval, INIParse) for (tkey, tval)
                           in val.items()):
                    string += "[" + key + "]\n"
                string += self._section_stringify(val, key)
            else:
                string += key + self.delimiters[0] + str(val) + "\n"
        return string
