from __future__ import print_function
import argparse
from collections import Counter
from datetime import datetime
import os
import sys
from utility import utilcsv

try:
    import xlsxwriter
except ImportError:
    print("[-] Install required third-party module xlsxwriter")
    sys.exit(1)

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
__description__ = "Create charts in XLSX files"


def main(output_directory):
    print("[+] Reading in sample data set")
    # Skip first row of headers
    data = utilcsv.csv_reader("redacted_sample_event_log.csv")[1:]
    xlsx_writer(data, output_directory)


def xlsx_writer(data, output_directory):
    print("[+] Writing output.xlsx file to {}".format(output_directory))
    workbook = xlsxwriter.Workbook(
        os.path.join(output_directory, "output.xlsx"))
    dashboard = workbook.add_worksheet("Dashboard")
    data_sheet = workbook.add_worksheet("Data")

    title_format = workbook.add_format({
        'bold': True, 'font_color': 'white', 'bg_color': 'black',
        'font_size': 30, 'font_name': 'Calibri', 'align': 'center'
    })
    date_format = workbook.add_format(
        {'num_format': 'mm/dd/yy hh:mm:ss AM/PM'})

    # Write CSV data to Data worksheet
    for i, record in enumerate(data):
        data_sheet.write_number(i, 0, int(record[0]))
        data_sheet.write(i, 1, record[1])
        data_sheet.write(i, 2, record[2])
        dt = datetime.strptime(record[3], "%m/%d/%Y %H:%M:%S %p")
        data_sheet.write_datetime(i, 3, dt, date_format)
        data_sheet.write_number(i, 4, int(record[4]))
        data_sheet.write(i, 5, record[5])
        data_sheet.write_number(i, 6, int(record[6]))
        data_sheet.write(i, 7, record[7])

    data_length = len(data) + 1
    data_sheet.add_table(
        "A1:H{}".format(data_length),
        {"columns": [
            {"header": "Index"},
            {"header": "File Name"},
            {"header": "Computer Name"},
            {"header": "Written Date"},
            {"header": "Event Level"},
            {"header": "Event Source"},
            {"header": "Event ID"},
            {"header": "File Path"}
        ]}
    )

    event_ids = Counter([x[6] for x in data])
    dashboard.merge_range('A1:Q1', 'Event Log Dashboard', title_format)
    for i, record in enumerate(event_ids):
        dashboard.write(100 + i, 0, record)
        dashboard.write(100 + i, 1, event_ids[record])

    dashboard.add_table("A100:B{}".format(
        100 + len(event_ids)),
        {"columns": [{"header": "Event ID"}, {"header": "Occurrence"}]}
    )

    event_chart = workbook.add_chart({'type': 'bar'})
    event_chart.set_title({'name': 'Event ID Breakdown'})
    event_chart.set_size({'x_scale': 2, 'y_scale': 5})

    event_chart.add_series(
        {'categories': '=Dashboard!$A$101:$A${}'.format(
            100 + len(event_ids)),
         'values': '=Dashboard!$B$101:$B${}'.format(
             100 + len(event_ids))})
    dashboard.insert_chart('C5', event_chart)

    workbook.close()


if __name__ == "__main__":
    # Command-line Argument Parser
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("OUTPUT_DIR", help="Desired Output Path")
    args = parser.parse_args()

    if not os.path.exists(args.OUTPUT_DIR):
        os.makedirs(args.OUTPUT_DIR)

    main(args.OUTPUT_DIR)
