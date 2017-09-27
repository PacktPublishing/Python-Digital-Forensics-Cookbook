from __future__ import print_function
import argparse
from datetime import datetime as dt
import os
import pytz
from pywintypes import Time
import shutil
from win32file import SetFileTime, CreateFile, CloseHandle
from win32file import GENERIC_WRITE, FILE_SHARE_WRITE
from win32file import OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL

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
__description__ = "Utility to copy files and associated metadata on Windows"

parser = argparse.ArgumentParser(
    description=__description__,
    epilog="Developed by {} on {}".format(
        ", ".join(__authors__), __date__)
)
parser.add_argument("source", help="Source file")
parser.add_argument("dest", help="Destination directory or file")
parser.add_argument("--timezone", help="Timezone of the file's timestamp",
                    choices=['EST5EDT', 'CST6CDT', 'MST7MDT', 'PST8PDT'],
                    required=True)
args = parser.parse_args()

source = os.path.abspath(args.source)
if os.sep in args.source:
    src_file_name = args.source.split(os.sep, 1)[1]
else:
    src_file_name = args.source

dest = os.path.abspath(args.dest)
tz = pytz.timezone(args.timezone)

shutil.copy2(source, dest)
if os.path.isdir(dest):
    dest_file = os.path.join(dest, src_file_name)
else:
    dest_file = dest

created = dt.fromtimestamp(os.path.getctime(source))
created = Time(tz.localize(created))
modified = dt.fromtimestamp(os.path.getmtime(source))
modified = Time(tz.localize(modified))
accessed = dt.fromtimestamp(os.path.getatime(source))
accessed = Time(tz.localize(accessed))

print("Source\n======")
print("Created:  {}\nModified: {}\nAccessed: {}".format(
    created, modified, accessed))

handle = CreateFile(dest_file, GENERIC_WRITE, FILE_SHARE_WRITE,
                    None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)
SetFileTime(handle, created, accessed, modified)
CloseHandle(handle)

created = tz.localize(dt.fromtimestamp(os.path.getctime(dest_file)))
modified = tz.localize(dt.fromtimestamp(os.path.getmtime(dest_file)))
accessed = tz.localize(dt.fromtimestamp(os.path.getatime(dest_file)))
print("\nDestination\n===========")
print("Created:  {}\nModified: {}\nAccessed: {}".format(
    created, modified, accessed))
