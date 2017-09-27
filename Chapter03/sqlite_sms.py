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
__description__ = "SQLite SMS analysis utility"


def main(database, out_csv):
    print("[+] Attempting connection to {} database".format(database))
    if not os.path.exists(database) or not os.path.isfile(database):
        print("[-] Database does not exist or is not a file")
        sys.exit(1)

    # Connect to SQLite Database
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Query DB for Column Names and Data of Message Table
    c.execute("pragma table_info(message)")
    table_data = c.fetchall()
    columns = [x[1] for x in table_data]

    c.execute("select * from message")
    message_data = c.fetchall()

    print("[+] Writing Message Content to {}".format(out_csv))
    write_csv(out_csv, columns, message_data)


def write_csv(output, cols, msgs):
    with open(output, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(cols)
        csv_writer.writerows(msgs)


if __name__ == '__main__':
    # Command-line Argument Parser
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("SQLITE_DATABASE", help="Input SQLite database")
    parser.add_argument("OUTPUT_CSV", help="Output CSV File")
    args = parser.parse_args()

    directory = os.path.dirname(args.OUTPUT_CSV)
    if directory != '' and not os.path.exists(directory):
        os.makedirs(directory)

    main(args.SQLITE_DATABASE, args.OUTPUT_CSV)
