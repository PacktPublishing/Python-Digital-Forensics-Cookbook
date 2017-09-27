from __future__ import print_function
import csv
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


def csv_writer(data, header, output_directory, name=None):
    if name is None:
        name = "output.csv"

    if sys.version_info < (3, 0):
        with open(os.path.join(output_directory, name), "wb") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            writer.writerows(data)
    else:
        with open(os.path.join(output_directory, name), "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            writer.writerows(data)


def csv_reader(f_path):
    if sys.version_info < (3, 0):
        with open(f_path, "rb") as csvfile:
            reader = csv.reader(csvfile)

            return list(reader)
    else:
        with open(f_path, newline="") as csvfile:
            reader = csv.reader(csvfile)

            return list(reader)


def unicode_csv_dict_writer(data, header, output_directory, name=None):
    try:
        import unicodecsv
    except ImportError:
        print("[+] Install unicodecsv module before executing this function")
        sys.exit(1)

    if name is None:
        name = "output.csv"

    print("[+] Writing {} to {}".format(name, output_directory))
    with open(os.path.join(output_directory, name), "wb") as csvfile:
        writer = unicodecsv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()

        writer.writerows(data)
