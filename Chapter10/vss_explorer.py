from __future__ import print_function
import argparse
from datetime import datetime, timedelta
import os
import pytsk3
import pyewf
import pyvshadow
import sys
import unicodecsv as csv
from utility import vss
from utility.pytskutil import TSKUtil
from utility import pytskutil

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
__description__ = "Utility to explore VSS on NTFS volumes"


def main(evidence, output):
    # Create TSK object and query path for prefetch files
    tsk_util = TSKUtil(evidence, "raw")
    img_vol = tsk_util.return_vol()
    if img_vol is not None:
        for part in img_vol:
            if tsk_util.detect_ntfs(img_vol, part):
                print("Exploring NTFS Partition for VSS")
                explore_vss(evidence, part.start * img_vol.info.block_size,
                            output)
    else:
        print("[-] Must be a physical preservation to be compatible "
              "with this script")
        sys.exit(2)


def explore_vss(evidence, part_offset, output):
    vss_volume = pyvshadow.volume()
    vss_handle = vss.VShadowVolume(evidence, part_offset)
    vss_count = vss.GetVssStoreCount(evidence, part_offset)
    if vss_count > 0:
        vss_volume.open_file_object(vss_handle)
        vss_data = []
        for x in range(vss_count):
            print("Gathering data for VSC {} of {}".format(x, vss_count))
            vss_store = vss_volume.get_store(x)
            image = vss.VShadowImgInfo(vss_store)
            vss_data.append(pytskutil.openVSSFS(image, x))

        write_csv(vss_data, output)


def write_csv(data, output):
    if data == []:
        print("[-] No output results to write")
        sys.exit(3)

    print("[+] Writing output to {}".format(output))
    if os.path.exists(output):
        append = True
    with open(output, "ab") as csvfile:
        csv_writer = csv.writer(csvfile)
        headers = ["VSS", "File", "File Ext", "File Type", "Create Date",
                   "Modify Date", "Change Date", "Size", "File Path"]
        if not append:
            csv_writer.writerow(headers)
        for result_list in data:
            csv_writer.writerows(result_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("EVIDENCE_FILE", help="Evidence file path")
    parser.add_argument("OUTPUT_CSV",
                        help="Output CSV with VSS file listing")
    args = parser.parse_args()

    directory = os.path.dirname(args.OUTPUT_CSV)
    if not os.path.exists(directory) and directory != "":
        os.makedirs(directory)

    if os.path.exists(args.EVIDENCE_FILE) and \
            os.path.isfile(args.EVIDENCE_FILE):
        main(args.EVIDENCE_FILE, args.OUTPUT_CSV)
    else:
        print("[-] Supplied input file {} does not exist or is not a "
              "file".format(args.EVIDENCE_FILE))
        sys.exit(1)
