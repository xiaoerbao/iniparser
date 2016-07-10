#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import iniparse
import json
ini = iniparse.INIParse()
ini.read("./test.ini")
print(json.dumps(ini))
print("=" * 40)