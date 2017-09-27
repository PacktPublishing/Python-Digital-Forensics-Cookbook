from __future__ import print_function
import argparse
from datetime import datetime
import os
import sys
import html_dashboard

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
__description__ = "Read FTK acquisition logs into a HTML dashboard"


def main(in_dir, out_dir):
    ftk_logs = [x for x in os.listdir(in_dir)
                if x.lower().endswith(".txt")]
    print("[+] Processing {} potential FTK Imager Logs found in {} "
          "directory".format(len(ftk_logs), in_dir))
    ftk_data = []
    for log in ftk_logs:
        log_data = {"e_numb": "", "custodian": "", "type": "",
                    "date": "", "size": ""}
        log_name = os.path.join(in_dir, log)
        if validate_ftk(log_name):
            with open(log_name) as log_file:
                bps, sec_count = (None, None)
                for line in log_file:
                    if "Evidence Number:" in line:
                        log_data["e_numb"] = line.split(
                            "Number:")[1].strip()
                    elif "Notes:" in line:
                        log_data["custodian"] = line.split(
                            "Notes:")[1].strip()
                    elif "Image Type:" in line:
                        log_data["type"] = line.split("Type:")[1].strip()
                    elif "Acquisition started:" in line:
                        acq = line.split("started:")[1].strip()
                        date = datetime.strptime(
                            acq, "%a %b %d %H:%M:%S %Y")
                        log_data["date"] = date.strftime(
                            "%M/%d/%Y %H:%M:%S")
                    elif "Bytes per Sector:" in line:
                        bps = int(line.split("Sector:")[1].strip())
                    elif "Sector Count:" in line:
                        sec_count = int(
                            line.split("Count:")[1].strip().replace(
                                ",", "")
                        )
                if bps is not None and sec_count is not None:
                    log_data["size"] = calculate_size(bps, sec_count)

            ftk_data.append(
                [log_data["e_numb"], log_data["custodian"],
                 log_data["type"], log_data["date"], log_data["size"]]
            )

    print("[+] Creating HTML dashboard based acquisition logs "
          "in {}".format(out_dir))
    html_dashboard.process_data(ftk_data, out_dir)


def validate_ftk(log_file):
    with open(log_file) as log:
        first_line = log.readline()
        if "Created By AccessData" not in first_line:
            return False
        else:
            return True


def calculate_size(bytes, sectors):
    return (bytes * sectors) / (1024**3)


if __name__ == "__main__":
    # Command-line Argument Parser
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("INPUT_DIR", help="Input Directory of Logs")
    parser.add_argument("OUTPUT_DIR", help="Desired Output Path")
    args = parser.parse_args()

    if os.path.exists(args.INPUT_DIR) and os.path.isdir(args.INPUT_DIR):
        main(args.INPUT_DIR, args.OUTPUT_DIR)
    else:
        print("[-] Supplied input directory {} does not exist or is not "
              "a file".format(args.INPUT_DIR))
        sys.exit(1)
