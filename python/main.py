#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import iniparser
import json
ini = iniparser.INIParser()
ini.read("./test.ini")
print(json.dumps(ini))
print("=" * 40)
