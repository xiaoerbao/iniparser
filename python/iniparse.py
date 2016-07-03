#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A INI file parser
"""

version = "0.0.1"
version_info = (0, 0, 1)


class INIParse:

    def __init__(self):
        pass

    def read(self, filenames, encoding=None):
        if isinstance(filenames, str):
            filenames = [filenames]
        read_ok = []
        for filename in filenames:
            try:
                with open(filename, encoding=encoding) as fp:
                    self._read(fp, filename)
            except OSError:
                continue
            read_ok.append(filename)
        return read_ok

    def read_file(self, f, source=None):
        if source is None:
            try:
                source = f.name
            except AttributeError:
                source = '<???>'
        self._read(f, source)

    def read_string(self, string, source='<string>'):
        """Read configuration from a given string."""
        sfile = io.StringIO(string)
        self.read_file(sfile, source)

    def read_dict(self, dictionary, source='<dict>'):
        pass

    def _read(self, fp, fpname):
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
