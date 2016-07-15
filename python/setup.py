#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = "1.0.1"
setup(
    name="INIParser",
    version=VERSION,
    description="A INIParser .",
    long_description='INI file format parsing just on Python3',
    keywords='INI parse parser',
    author='laoma',
    author_email='laomafeima@gmail.com',
    url='https://github.com/laomafeima/iniparse',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    packages=find_packages(),
    py_modules=["iniparser"],
    )
