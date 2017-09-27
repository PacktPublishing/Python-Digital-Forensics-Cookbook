from __future__ import print_function
import argparse
import csv
import os
import sqlite3
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
__description__ = "Utility to extract reports from IEF"


def main(database, out_directory):
    print("[+] Connecting to SQLite database")
    conn = sqlite3.connect(database)
    c = conn.cursor()

    print("[+] Querying IEF database for list of all tables to extract")
    c.execute("select * from sqlite_master where type='table'")
    # Remove tables that start with "_" or end with "_DATA"
    tables = [x[2] for x in c.fetchall() if not x[2].startswith('_') and
              not x[2].endswith('_DATA')]

    print("[+] Dumping {} tables to CSV files in {}".format(
        len(tables), out_directory))
    for table in tables:
        c.execute("pragma table_info('{}')".format(table))
        table_columns = [x[1] for x in c.fetchall()]
        c.execute("select * from '{}'".format(table))
        table_data = c.fetchall()

        csv_name = table + '.csv'
        csv_path = os.path.join(out_directory, csv_name)
        print('[+] Writing {} table to {} CSV file'.format(table,
                                                           csv_name))
        with open(csv_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(table_columns)
            csv_writer.writerows(table_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("IEF_DATABASE", help="Input IEF database")
    parser.add_argument("OUTPUT_DIR", help="Output DIR")
    args = parser.parse_args()

    if not os.path.exists(args.OUTPUT_DIR):
        os.makedirs(args.OUTPUT_DIR)

    if os.path.exists(args.IEF_DATABASE) and \
            os.path.isfile(args.IEF_DATABASE):
        main(args.IEF_DATABASE, args.OUTPUT_DIR)
    else:
        print("[-] Supplied input file {} does not exist or is not a "
              "file".format(args.IEF_DATABASE))
        sys.exit(1)
