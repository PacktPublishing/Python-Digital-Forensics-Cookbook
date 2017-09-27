from __future__ import print_function
import argparse
from datetime import datetime, timedelta
import os
import pytsk3
import pyewf
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
__description__ = " Read information from prefetch files"


def main(evidence, image_type, output_csv, path):
    # Create TSK object and query path for prefetch files
    tsk_util = TSKUtil(evidence, image_type)
    prefetch_dir = tsk_util.query_directory(path)
    prefetch_files = None
    if prefetch_dir is not None:
        prefetch_files = tsk_util.recurse_files(
            ".pf", path=path, logic="endswith")
    if prefetch_files is None:
        print("[-] No .pf files found")
        sys.exit(2)

    print("[+] Identified {} potential prefetch files".format(
          len(prefetch_files)))
    prefetch_data = []
    for hit in prefetch_files:
        prefetch_file = hit[2]
        pf_version = check_signature(prefetch_file)
        if pf_version is None:
            continue

        pf_name = hit[0]
        if pf_version == 17:
            parsed_data = parse_pf_17(prefetch_file, pf_name)
            parsed_data.append(os.path.join(path, hit[1].lstrip("//")))
            prefetch_data.append(parsed_data)

        elif pf_version == 23:
            print("[-] Windows Vista / 7 PF file {} -- unsupported".format(
                pf_name))
            continue
        elif pf_version == 26:
            print("[-] Windows 8 PF file {} -- unsupported".format(
                pf_name))
            continue
        elif pf_version == 30:
            print("[-] Windows 10 PF file {} -- unsupported".format(
                pf_name))
            continue

        else:
            print("[-] Signature mismatch - Name: {}\nPath: {}".format(
                hit[0], hit[1]))
            continue

    write_output(prefetch_data, output_csv)


def parse_pf_17(prefetch_file, pf_name):
    # Parse Windows XP, 2003 Prefetch File
    create = convert_unix(prefetch_file.info.meta.crtime)
    modify = convert_unix(prefetch_file.info.meta.mtime)

    pf_size, name, vol_info, vol_entries, vol_size, filetime, \
        count = struct.unpack("<i60s32x3iq16xi",
                              prefetch_file.read_random(12, 136))

    name = name.decode("utf-16", "ignore").strip("/x00").split("/x00")[0]

    vol_name_offset, vol_name_length, vol_create, \
        vol_serial = struct.unpack("<2iqi",
                                   prefetch_file.read_random(vol_info, 20))

    vol_serial = hex(vol_serial).lstrip("0x")
    vol_serial = vol_serial[:4] + "-" + vol_serial[4:]

    vol_name = struct.unpack(
        "<{}s".format(2 * vol_name_length),
        prefetch_file.read_random(vol_info + vol_name_offset,
                                  vol_name_length * 2)
    )[0]

    vol_name = vol_name.decode("utf-16", "ignore").strip("/x00").split(
        "/x00")[0]

    return [
        pf_name, name, pf_size, create,
        modify, convert_filetime(filetime), count, vol_name,
        convert_filetime(vol_create), vol_serial
    ]


def convert_unix(ts):
    if int(ts) == 0:
        return ""
    return datetime.utcfromtimestamp(ts)


def convert_filetime(ts):
    if int(ts) == 0:
        return ""
    return datetime(1601, 1, 1) + timedelta(microseconds=ts / 10)


def check_signature(prefetch_file):
    version, signature = struct.unpack(
        "<2i", prefetch_file.read_random(0, 8))

    if signature == 1094927187:
        return version
    else:
        return None


def write_output(data, output_csv):
    print("[+] Writing csv report")
    with open(output_csv, "wb") as outfile:
        writer = csv.writer(outfile)
        writer.writerow([
            "File Name", "Prefetch Name", "File Size (bytes)",
            "File Create Date (UTC)", "File Modify Date (UTC)",
            "Prefetch Last Execution Date (UTC)",
            "Prefetch Execution Count", "Volume", "Volume Create Date",
            "Volume Serial", "File Path"
        ])
        writer.writerows(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("EVIDENCE_FILE", help="Evidence file path")
    parser.add_argument("TYPE", help="Type of Evidence",
                        choices=("raw", "ewf"))
    parser.add_argument("OUTPUT_CSV", help="Path to write output csv")
    parser.add_argument("-d", help="Prefetch directory to scan",
                        default="/WINDOWS/PREFETCH")
    args = parser.parse_args()

    if os.path.exists(args.EVIDENCE_FILE) and \
            os.path.isfile(args.EVIDENCE_FILE):
        main(args.EVIDENCE_FILE, args.TYPE, args.OUTPUT_CSV, args.d)
    else:
        print("[-] Supplied input file {} does not exist or is not a "
              "file".format(args.EVIDENCE_FILE))
        sys.exit(1)
