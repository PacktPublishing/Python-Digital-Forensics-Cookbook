from __future__ import print_function
from argparse import ArgumentParser, FileType
from datetime import datetime
import csv

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
__description__ = "Utility to interpret the daily.out log"


class ProcessDailyOut(object):
    def __init__(self, daily_out):
        self.daily_out = daily_out
        self.disk_status_columns = [
            'Filesystem', 'Size', 'Used', 'Avail', 'Capacity', 'iused',
            'ifree', '%iused', 'Mounted on']
        self.report_columns = ['event_date', 'event_tz'] + \
            self.disk_status_columns

    def process_disk(self, disk_lines, event_dates):
        if len(disk_lines) == 0:
            return {}

        processed_data = []
        for line_count, line in enumerate(disk_lines):
            if line_count == 0:
                continue
            prepped_lines = [x for x in line.split(" ")
                             if len(x.strip()) != 0]
            disk_info = {
                "event_date": event_dates[0],
                "event_tz": event_dates[1]
            }
            for col_count, entry in enumerate(prepped_lines):
                curr_col = self.disk_status_columns[col_count]
                if "/Volumes/" in entry:
                    disk_info[curr_col] = " ".join(
                        prepped_lines[col_count:])
                    break
                disk_info[curr_col] = entry.strip()
            processed_data.append(disk_info)
        return processed_data

    def process_event(self, event_lines):
        section_header = ""
        section_data = []
        event_data = {}
        for line in event_lines:
            if line.endswith(":"):
                if len(section_data) > 0:
                    event_data[section_header] = section_data
                    section_data = []
                    section_header = ""

                section_header = line.strip(":")

            elif line.count(":") == 2:
                try:
                    split_line = line.split()
                    timezone = split_line[4]
                    date_str = " ".join(split_line[:4] + [split_line[-1]])
                    try:
                        date_val = datetime.strptime(
                            date_str, "%a %b %d %H:%M:%S %Y")
                    except ValueError:
                        date_val = datetime.strptime(
                            date_str, "%a %b  %d %H:%M:%S %Y")
                    event_data["event_date"] = [date_val, timezone]
                    section_data = []
                    section_header = ""
                except ValueError:
                    section_data.append(line)
                except IndexError:
                    section_data.append(line)

            else:
                if len(line):
                    section_data.append(line)
        return self.process_disk(event_data.get("Disk status", []),
                                 event_data.get("event_date", []))

    def run(self):
        event_lines = []
        parsed_events = []
        for raw_line in self.daily_out:
            line = raw_line.strip()
            if line == '-- End of daily output --':
                parsed_events += self.process_event(event_lines)
                event_lines = []
            else:
                event_lines.append(line)
        return parsed_events


def write_csv(outfile, fieldnames, data):
    with open(outfile, 'w', newline="") as open_outfile:
        csvfile = csv.DictWriter(open_outfile, fieldnames)
        csvfile.writeheader()
        csvfile.writerows(data)


if __name__ == '__main__':
    parser = ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("daily_out", help="Path to daily.out file",
                        type=FileType('r'))
    parser.add_argument("output_report", help="Path to csv report")
    args = parser.parse_args()

    processor = ProcessDailyOut(args.daily_out)
    parsed_events = processor.run()
    write_csv(args.output_report, processor.report_columns, parsed_events)
