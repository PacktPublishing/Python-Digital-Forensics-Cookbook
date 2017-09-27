from __future__ import print_function
import argparse
from datetime import datetime, timedelta
import os
import pytsk3
import pyewf
import pyesedb
import struct
import sys
import unicodecsv as csv
from utility.pytskutil import TSKUtil

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
__description__ = "Extract information from the SRUM database"

TABLE_LOOKUP = {
    "{973F5D5C-1D90-4944-BE8E-24B94231A174}": "Network Data Usage",
    "{D10CA2FE-6FCF-4F6D-848E-B2E99266FA86}": "Push Notifications",
    "{D10CA2FE-6FCF-4F6D-848E-B2E99266FA89}": "Application Resource Usage",
    "{DD6636C4-8929-4683-974E-22C046A43763}": "Network Connectivity Usage",
    "{FEE4E14F-02A9-4550-B5CE-5FA2DA202E37}": "Energy Usage"}

APP_ID_LOOKUP = {}


def main(evidence, image_type):
    # Create TSK object and query for Internet Explorer index.dat files
    tsk_util = TSKUtil(evidence, image_type)
    path = "/Windows/System32/sru"
    srum_dir = tsk_util.query_directory(path)
    if srum_dir is not None:
        srum_files = tsk_util.recurse_files("SRUDB.dat", path=path,
                                            logic="equal")
        if srum_files is not None:
            print("[+] Identified {} potential SRUDB.dat file(s)".format(
                len(srum_files)))
            for hit in srum_files:
                srum_file = hit[2]
                srum_tables = {}
                temp_srum = write_file(srum_file)
                if pyesedb.check_file_signature(temp_srum):
                    srum_dat = pyesedb.open(temp_srum)
                    print("[+] Process {} tables within database".format(
                        srum_dat.number_of_tables))
                    for table in srum_dat.tables:
                        if table.name != "SruDbIdMapTable":
                            continue
                        global APP_ID_LOOKUP
                        for entry in table.records:
                            app_id = entry.get_value_data_as_integer(1)
                            try:
                                app = entry.get_value_data(2).replace(
                                    "\x00", "")
                            except AttributeError:
                                app = ""
                            APP_ID_LOOKUP[app_id] = app

                    for table in srum_dat.tables:
                        t_name = table.name
                        print("[+] Processing {} table with {} records"
                              .format(t_name, table.number_of_records))
                        srum_tables[t_name] = {"columns": [], "data": []}
                        columns = [x.name for x in table.columns]
                        srum_tables[t_name]["columns"] = columns
                        for entry in table.records:
                            data = []
                            for x in range(entry.number_of_values):
                                data.append(convert_data(
                                    entry.get_value_data(x), columns[x],
                                    entry.get_column_type(x))
                                )
                            srum_tables[t_name]["data"].append(data)
                        write_output(t_name, srum_tables)

                else:
                    print("[-] {} not a valid SRUDB.dat file. Removing "
                          "temp file...".format(temp_srum))
                    os.remove(temp_srum)
                    continue

        else:
            print("[-] SRUDB.dat files not found in {} "
                  "directory".format(path))
            sys.exit(3)

    else:
        print("[-] Directory {} not found".format(path))
        sys.exit(2)


def convert_data(data, column, col_type):
    if data is None:
        return ""
    elif column == "AppId":
        return APP_ID_LOOKUP[struct.unpack("<i", data)[0]]
    elif col_type == 0:
        return ""
    elif col_type == 1:
        if data == "*":
            return True
        else:
            return False
    elif col_type == 2:
        return struct.unpack("<B", data)[0]
    elif col_type == 3:
        return struct.unpack("<h", data)[0]
    elif col_type == 4:
        return struct.unpack("<i", data)[0]
    elif col_type == 6:
        return struct.unpack("<f", data)[0]
    elif col_type == 7:
        return struct.unpack("<d", data)[0]
    elif col_type == 8:
        return convert_ole(struct.unpack("<q", data)[0])
    elif col_type in [5, 9, 10, 12, 13, 16]:
        return data
    elif col_type == 11:
        return data.replace("\x00", "")
    elif col_type == 14:
        return struct.unpack("<I", data)[0]
    elif col_type == 15:
        if column in ["EventTimestamp", "ConnectStartTime"]:
            return convert_filetime(struct.unpack("<q", data)[0])
        else:
            return struct.unpack("<q", data)[0]
    elif col_type == 17:
        return struct.unpack("<H", data)[0]
    else:
        return data


def write_file(srum_file):
    with open(srum_file.info.name.name, "w") as outfile:
        outfile.write(srum_file.read_random(0, srum_file.info.meta.size))
    return srum_file.info.name.name


def convert_filetime(ts):
    if str(ts) == "0":
        return ""
    try:
        dt = datetime(1601, 1, 1) + timedelta(microseconds=ts / 10)
    except OverflowError:
        return ts
    return dt


def convert_ole(ts):
    ole = struct.unpack(">d", struct.pack(">Q", ts))[0]
    try:
        dt = datetime(1899, 12, 30, 0, 0, 0) + timedelta(days=ole)
    except OverflowError:
        return ts
    return dt


def write_output(table, data):
    if len(data[table]["data"]) == 0:
        return
    if table in TABLE_LOOKUP:
        output_name = TABLE_LOOKUP[table] + ".csv"
    else:
        output_name = "SRUM_Table_{}.csv".format(table)
    print("[+] Writing {} to current working directory: {}".format(
        output_name, os.getcwd()))
    with open(output_name, "wb") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(data[table]["columns"])
        writer.writerows(data[table]["data"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("EVIDENCE_FILE", help="Evidence file path")
    parser.add_argument("TYPE", help="Type of Evidence",
                        choices=("raw", "ewf"))
    args = parser.parse_args()

    if os.path.exists(args.EVIDENCE_FILE) and os.path.isfile(
            args.EVIDENCE_FILE):
        main(args.EVIDENCE_FILE, args.TYPE)
    else:
        print("[-] Supplied input file {} does not exist or is not a "
              "file".format(args.EVIDENCE_FILE))
        sys.exit(1)
