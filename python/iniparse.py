#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import os
"""
A INI file parser
"""

version = "0.0.1"
version_info = (0, 0, 1)


class INIParse:

    def __init__(self):
        self._comment_symbol = [";"]
        self._section_symbol = ("[", "]")
        self._include_symbol = "@include "
        self._delimiters = (";", "=")
        self._section_delimiters = "."
        self._file_list = []
        self._read_file_list = []
        self._result_dict = {}

    def read(self, filenames, encoding=None):
        if isinstance(filenames, str):
            filenames = [filenames]
        for filename in filenames:
            try:
                with open(filename, encoding=encoding) as fp:
                    self._read(fp, filename)
            except OSError:
                continue
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

    def read_dict(self, dictionary, source='<dict>'):
        pass

    def _read(self, fp, fpname):
        self._file_list.append(fpname)
        for line in fp:
            line = line.strip()
            if len(line) < 1 or line[0] in self._comment_symbol:
                continue
            if line.lower().startswith(self._include_symbol):
                self._parse_include(line, fp)
                continue
            if all(symbol in line for symbol in self._section_symbol):
                self._parse_section(line)
                continue
            if any(symbol in line for symbol in self._delimiters):
                self._parse_expression(line)

    def _parse_include(self, line, fp):
        filename = line[len(self._include_symbol):]
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
        line = line.strip("[").strip("]")
        while self._section_delimiters in line:
            index = line.index(self._section_delimiters)
            group = line[0:index]
            self._result_dict[group] = {}
            line = line[index + 1:]
        print(self._result_dict)

    def _parse_expression(self, line):
        pass

    def refresh(self):
        pass

    def sections(self):
        pass

    def get_section(self):
        pass

    def set_sections(self):
        pass

    def write_file(self):
        pass

    def stringify(self):
        pass


class Section(dict):

    def __init__(self):
        pass


class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)
