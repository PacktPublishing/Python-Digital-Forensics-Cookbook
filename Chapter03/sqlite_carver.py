from __future__ import print_function
import argparse
import binascii
import csv
from itertools import product
import os
import re
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
__description__ = "SQLite carving utility"


def main(database, table, out_csv, **kwargs):
    print("[+] Attempting connection to {} database".format(database))
    if not os.path.exists(database) or not os.path.isfile(database):
        print("[-] Database does not exist or is not a file")
        sys.exit(1)

    # Connect to SQLite Database
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # Query Table for Primary Key
    c.execute("pragma table_info({})".format(table))
    table_data = c.fetchall()
    if table_data == []:
        print("[-] Check spelling of table name - '{}' did not return "
              "any results".format(table))
        sys.exit(2)

    if "col" in kwargs:
        gaps = find_gaps(c, table, kwargs["col"])

    else:
        # Add Primary Keys to List
        potential_pks = []
        for row in table_data:
            if row[-1] == 1:
                potential_pks.append(row[1])

        if len(potential_pks) <= 0 or len(potential_pks) >= 2:
            print("[-] None or multiple primary keys found -- please check "
                  "if there is a primary key or specify a specific key "
                  "using the --column argument")
            sys.exit(3)

        gaps = find_gaps(c, table, potential_pks[0])
    conn.close()

    print("[+] Carving for missing ROWIDs")
    varints = varint_converter(list(gaps))
    search_results = find_candidates(database, varints)
    if search_results != []:
        print("[+] Writing {} potential candidates to {}".format(
            len(search_results), out_csv))
        write_csv(out_csv, ["ROWID", "Search Term", "Offset"],
                  search_results)
    else:
        print("[-] No search results found for missing ROWIDs")


def find_gaps(db_conn, table, pk):
    print("[+] Identifying missing ROWIDs for {} column".format(pk))
    try:
        db_conn.execute("select {} from {}".format(pk, table))
    except sqlite3.OperationalError:
        print("[-] '{}' column does not exist -- "
              "please check spelling".format(pk))
        sys.exit(4)
    results = db_conn.fetchall()
    rowids = sorted([x[0] for x in results])
    total_missing = rowids[-1] - len(rowids)

    if total_missing == 0:
        print("[*] No missing ROWIDs from {} column".format(pk))
        sys.exit(0)
    else:
        print("[+] {} missing ROWID(s) from {} column".format(
            total_missing, pk))

    # Find Missing ROWIDs
    gaps = set(range(rowids[0], rowids[-1] + 1)).difference(rowids)
    return gaps


def varint_converter(rows):
    varints = {}
    varint_combos = []
    for i, row in enumerate(rows):
        if row <= 127:
            varints[hex(row)[2:]] = row

        else:
            combos = [x for x in range(0, 256)]
            counter = 1
            while True:
                counter += 1
                print("[+] Generating and finding all {} byte "
                      "varints..".format(counter))
                varint_combos = list(product(combos, repeat=counter))
                varint_combos = [x for x in varint_combos if x[0] >= 128]
                for varint_combo in varint_combos:
                    varint = integer_converter(varint_combo)
                    if varint == row:
                        varints["".join([hex(v)[2:].zfill(2) for v in
                                         varint_combo])] = row
                        i += 1
                        try:
                            row = rows[i]
                        except IndexError:
                            return varints


def integer_converter(numbs):
    binary = ""
    for numb in numbs:
        binary += bin(numb)[2:].zfill(8)[1:]
    binvar = binary.lstrip("0")
    if binvar != '':
        return int(binvar, 2)
    else:
        return 0


def find_candidates(database, varints):
    results = []
    candidate_a = "350055"
    candidate_b = "360055"

    with open(database, "rb") as infile:
        hex_data = str(binascii.hexlify(infile.read()))
    for varint in varints:
        search_a = varint + candidate_a
        search_b = varint + candidate_b

        for result in re.finditer(search_a, hex_data):
            results.append([varints[varint], search_a, result.start() / 2])

        for result in re.finditer(search_b, hex_data):
            results.append([varints[varint], search_b, result.start() / 2])

    return results


def write_csv(output, cols, msgs):
    with open(output, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(cols)
        csv_writer.writerows(msgs)


if __name__ == "__main__":
    # Command-line Argument Parser
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("SQLITE_DATABASE", help="Input SQLite database")
    parser.add_argument("TABLE", help="Table to query from")
    parser.add_argument("OUTPUT_CSV", help="Output CSV File")
    parser.add_argument("--column", help="Optional column argument")
    args = parser.parse_args()

    if args.column is not None:
        main(args.SQLITE_DATABASE, args.TABLE,
             args.OUTPUT_CSV, col=args.column)
    else:
        main(args.SQLITE_DATABASE, args.TABLE, args.OUTPUT_CSV)
