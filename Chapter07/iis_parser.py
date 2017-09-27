from __future__ import print_function
from argparse import ArgumentParser, FileType
import re
import shlex
import logging
import sys
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
__description__ = "Utility to parse IIS logs"
logger = logging.getLogger(__file__)

iis_log_format = [
    ("date", re.compile(r"\d{4}-\d{2}-\d{2}")),
    ("time", re.compile(r"\d\d:\d\d:\d\d")),
    ("s-ip", re.compile(
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}")),
    ("cs-method", re.compile(
        r"(GET)|(POST)|(PUT)|(DELETE)|(OPTIONS)|(HEAD)|(CONNECT)")),
    ("cs-uri-stem", re.compile(r"([A-Za-z0-1/\.-]*)")),
    ("cs-uri-query", re.compile(r"([A-Za-z0-1/\.-]*)")),
    ("s-port", re.compile(r"\d*")),
    ("cs-username", re.compile(r"([A-Za-z0-1/\.-]*)")),
    ("c-ip", re.compile(
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}")),
    ("cs(User-Agent)", re.compile(r".*")),
    ("sc-status", re.compile(r"\d*")),
    ("sc-substatus", re.compile(r"\d*")),
    ("sc-win32-status", re.compile(r"\d*")),
    ("time-taken", re.compile(r"\d*"))
]


def main(iis_log, report_file, logger):
    parsed_logs = []
    for raw_line in iis_log:
        line = raw_line.strip()
        log_entry = {}
        if line.startswith("#") or len(line) == 0:
            continue
        if '\"' in line:
            line_iter = shlex.shlex(line_iter)
        else:
            line_iter = line.split(" ")
        for count, split_entry in enumerate(line_iter):
            col_name, col_pattern = iis_log_format[count]
            if col_pattern.match(split_entry):
                log_entry[col_name] = split_entry
            else:
                logger.error("Unknown column pattern discovered. "
                             "Line preserved in full below")
                logger.error("Unparsed Line: {}".format(line))

        parsed_logs.append(log_entry)

    logger.info("Parsed {} lines".format(len(parsed_logs)))

    cols = [x[0] for x in iis_log_format]
    logger.info("Creating report file: {}".format(report_file))
    write_csv(report_file, cols, parsed_logs)
    logger.info("Report created")


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
    parser.add_argument('iis_log', help="Path to IIS Log",
                        type=FileType('r'))
    parser.add_argument('csv_report', help="Path to CSV report")
    parser.add_argument('-l', help="Path to processing log",
                        default=__name__ + '.log')
    args = parser.parse_args()

    logger.setLevel(logging.DEBUG)
    msg_fmt = logging.Formatter("%(asctime)-15s %(funcName)-10s "
                                "%(levelname)-8s %(message)s")

    strhndl = logging.StreamHandler(sys.stdout)
    strhndl.setFormatter(fmt=msg_fmt)
    fhndl = logging.FileHandler(args.log, mode='a')
    fhndl.setFormatter(fmt=msg_fmt)

    logger.addHandler(strhndl)
    logger.addHandler(fhndl)

    logger.info("Starting IIS Parsing ")
    logger.debug("Supplied arguments: {}".format(", ".join(sys.argv[1:])))
    logger.debug("System " + sys.platform)
    logger.debug("Version " + sys.version)
    main(args.iis_log, args.csv_report, logger)
    logger.info("IIS Parsing Complete")
