from __future__ import print_function
import argparse
from datetime import datetime as dt
import os
import sys

"""
MIT License

Copyright (c) 2017 Chapin Bryce, Preston Miller

Please share comments and questions at:
    https://github.com/PythonForensics/PythonForensicsCookbook
    or email pyforcookbook@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__authors__ = ["Chapin Bryce", "Preston Miller"]
__date__ = 20170815
__description__ = "Gather filesystem metadata of provided file"

parser = argparse.ArgumentParser(
    description=__description__,
    epilog="Developed by {} on {}".format(", ".join(__authors__), __date__)
)
parser.add_argument("FILE_PATH",
                    help="Path to file to gather metadata for")
args = parser.parse_args()
file_path = args.FILE_PATH

stat_info = os.stat(file_path)
if "linux" in sys.platform or "darwin" in sys.platform:
    print("Change time: ", dt.fromtimestamp(stat_info.st_ctime))
elif "win" in sys.platform:
    print("Creation time: ", dt.fromtimestamp(stat_info.st_ctime))
else:
    print("[-] Unsupported platform {} detected. Cannot interpret "
          "creation/change timestamp.".format(sys.platform)
          )
print("Modification time: ", dt.fromtimestamp(stat_info.st_mtime))
print("Access time: ", dt.fromtimestamp(stat_info.st_atime))

print("File mode: ", stat_info.st_mode)
print("File inode: ", stat_info.st_ino)
major = os.major(stat_info.st_dev)
minor = os.minor(stat_info.st_dev)
print("Device ID: ", stat_info.st_dev)
print("\tMajor: ", major)
print("\tMinor: ", minor)

print("Number of hard links: ", stat_info.st_nlink)
print("Owner User ID: ", stat_info.st_uid)
print("Group ID: ", stat_info.st_gid)
print("File Size: ", stat_info.st_size)

print("Is a symlink: ", os.path.islink(file_path))
print("Absolute Path: ", os.path.abspath(file_path))
print("File exists: ", os.path.exists(file_path))
print("Parent directory: ", os.path.dirname(file_path))
print("Parent directory: {} | File name: {}".format(
    *os.path.split(file_path)))
