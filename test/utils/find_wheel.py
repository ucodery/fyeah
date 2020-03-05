#! /usr/bin/env python
import os
import sys

from pip._internal.models.target_python import TargetPython

search_dir = sys.argv[1] if len(sys.argv) > 1 else './dist/'
wheels = os.listdir(search_dir)

for tag in TargetPython().get_tags():
    for wheel in wheels:
        if str(tag) in wheel:
            print(wheel)
            break
    else:
        continue
    break
