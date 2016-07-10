#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
"""
A INI file parser
"""

version = "0.0.1"
version_info = (0, 0, 1)


class INIParse(dict):

    def __init__(self):
        self.comment_symbol = [";"]
        self.section_symbol = ("[", "]")
        self.string_symbol = ("\"", "'")
        self.true_boolean_symbol = ("true",)
        self.false_boolean_symbol = ("false",)
        self.include_symbol = "@include "
        self.delimiters = ("=", ":")
        self.section_delimiters = "."
        self._file_list = []
        self._read_file_list = []
        self._read_file_encoding = None
        self._result_dict = {}
        self._cursor = {}

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def read(self, filenames, encoding=None):
        self._read_file_encoding = encoding
        if isinstance(filenames, str):
            filenames = [filenames]
        for filename in filenames:
            try:
                with open(filename, encoding=encoding) as fp:
                    self._read(fp, filename)
            except OSError:
                continue
            if filename not in self._read_file_list:
                self._read_file_list.append(filename)
        return self._read_file_list

    def read_file(self, f, source=None):
        if source is None:
            try:
                source = f.name
                self._read_file_list.append(source)
            except AttributeError:
                source = '<???>'
        self._read(f, source)

    def read_string(self, string, source='<string>'):
        """Read configuration from a given string."""
        sfile = io.StringIO(string)
        self._read(sfile, source)

    def read_dict(self, dictionary):
        self.update(dictionary)

    def _read(self, fp, fpname):
        self._file_list.append(fpname)
        for line in fp:
            line = line.strip()
            print(line)
            if len(line) < 1 or line[0] in self.comment_symbol:
                continue
            if line.lower().startswith(self.include_symbol):
                self._parse_include(line, fp)
                continue
            if all(symbol in line for symbol in self.section_symbol):
                self._parse_section(line)
                continue
            if any(symbol in line for symbol in self.delimiters):
                self._parse_expression(line)
        fp.close()

    def _parse_include(self, line, fp):
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
            elif value.isnumeric():
                value = int(value)
            else:
                try:
                    # 最后尝试做 float 转换
                    value = float(value)
                except ValueError:
                    pass
        # 赋值
        self._cursor[key] = value

    def _check_variable(self, variable, return_bool=True):
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
        result = self._check_variable(variable, False)
        if result["section"] is None:
            print("Error")
        else:
            return result["section"][result["variable"]]

    def refresh(self):
        self.clear()
        self.read(self._read_file_list)

    def sections(self):
        return self.keys()

    def get_section(self, section):
        if section in self:
            return self[section]
        else:
            return None

    def set_sections(self, section, dictionary):
        if section in self:
            self[section].update(dictionary)
        else:
            self[section] = dictionary

    def get_int(self, key):
        if self.has(key):
            return int(self[key])
        else:
            return False

    def get_float(self, key):
        if self.has(key):
            return float(self[key])
        else:
            return False

    def get_bool(self, key):
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
        if self.has(key):
            return str(self[key])
        else:
            return False

    def is_none(self, key):
        if self.has(key) and self[key] is None:
            return True
        else:
            return False

    def has(self, key):
        return True if key in self else False

    def write_file(self, f):
        string = self.stringify()
        return f.write(string)

    def stringify(self):
        return self._section_stringify(self)

    def _section_stringify(self, section, prefix=""):
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
