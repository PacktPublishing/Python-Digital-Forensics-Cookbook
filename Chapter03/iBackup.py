from __future__ import print_function
import argparse
import logging
import os
from shutil import copyfile
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
__description__ = "iOS 10 Backup Parser"

logger = logging.getLogger(__name__)


def main(in_dir, out_dir):
    backups = backup_summary(in_dir)

    print("Backup Summary")
    print("=" * 20)
    if len(backups) > 0:
        for i, b in enumerate(backups):
            print("Backup No.: {} \n"
                  "Backup Dev. Name: {} \n"
                  "# Files: {} \n"
                  "Backup Size (Bytes): {}\n".format(
                      i, b, backups[b][1], backups[b][2])
                  )
            try:
                db_items = process_manifest(backups[b][0])
            except IOError:
                logger.warn("Non-iOS 10 backup encountered or "
                            "invalid backup. Continuing to next backup.")
                continue

            create_files(in_dir, out_dir, b, db_items)
        print("=" * 20)

    else:
        logger.warning(
            "No valid backups found. The input directory should be "
            "the parent-directory immediately above the SHA-1 hash "
            "iOS device backups")
        sys.exit(2)


def backup_summary(in_dir):
    logger.info("Identifying all iOS backups in {}".format(in_dir))
    root = os.listdir(in_dir)
    backups = {}
    for x in root:
        temp_dir = os.path.join(in_dir, x)
        if os.path.isdir(temp_dir) and len(x) == 40:
            num_files = 0
            size = 0

            for root, subdir, files in os.walk(temp_dir):
                num_files += len(files)
                size += sum(os.path.getsize(os.path.join(root, name))
                            for name in files)

            backups[x] = [temp_dir, num_files, size]

    return backups


def process_manifest(backup):
    manifest = os.path.join(backup, "Manifest.db")

    if not os.path.exists(manifest):
        logger.error("Manifest DB not found in {}".format(manifest))
        raise IOError

    conn = sqlite3.connect(manifest)
    c = conn.cursor()
    items = {}
    for row in c.execute("SELECT * from Files;"):
        items[row[0]] = [row[2], row[1], row[3]]

    return items


def create_files(in_dir, out_dir, b, db_items):
    msg = "Copying Files for backup {} to {}".format(
        b, os.path.join(out_dir, b))
    logger.info(msg)
    files_not_found = 0
    for x, key in enumerate(db_items):
        if db_items[key][0] is None or db_items[key][0] == "":
            continue

        else:
            dirpath = os.path.join(
                out_dir, b, os.path.dirname(db_items[key][0]))
            filepath = os.path.join(out_dir, b, db_items[key][0])
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

            original_dir = b + "/" + key[0:2] + "/" + key
            path = os.path.join(in_dir, original_dir)

            if os.path.exists(filepath):
                filepath = filepath + "_{}".format(x)
            try:
                copyfile(path, filepath)
            except IOError:
                logger.debug("File not found in backup: {}".format(path))
                files_not_found += 1

    if files_not_found > 0:
        logger.warning("{} files listed in the Manifest.db not"
                       "found in backup".format(files_not_found))

    copyfile(os.path.join(in_dir, b, "Info.plist"),
             os.path.join(out_dir, b, "Info.plist"))
    copyfile(os.path.join(in_dir, b, "Manifest.db"),
             os.path.join(out_dir, b, "Manifest.db"))
    copyfile(os.path.join(in_dir, b, "Manifest.plist"),
             os.path.join(out_dir, b, "Manifest.plist"))
    copyfile(os.path.join(in_dir, b, "Status.plist"),
             os.path.join(out_dir, b, "Status.plist"))


if __name__ == "__main__":
    # Command-line Argument Parser
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument(
        "INPUT_DIR",
        help="Location of folder containing iOS backups, "
        "e.g. ~\Library\Application Support\MobileSync\Backup folder"
    )
    parser.add_argument("OUTPUT_DIR", help="Output Directory")
    parser.add_argument("-l", help="Log file path",
                        default=__file__[:-2] + "log")
    parser.add_argument("-v", help="Increase verbosity",
                        action="store_true")
    args = parser.parse_args()

    if args.v:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    msg_fmt = logging.Formatter("%(asctime)-15s %(funcName)-13s"
                                "%(levelname)-8s %(message)s")
    strhndl = logging.StreamHandler(sys.stderr)
    strhndl.setFormatter(fmt=msg_fmt)
    fhndl = logging.FileHandler(args.l, mode='a')
    fhndl.setFormatter(fmt=msg_fmt)

    logger.addHandler(strhndl)
    logger.addHandler(fhndl)

    logger.info("Starting iBackup Visualizer")
    logger.debug("Supplied arguments: {}".format(" ".join(sys.argv[1:])))
    logger.debug("System: " + sys.platform)
    logger.debug("Python Version: " + sys.version)

    if not os.path.exists(args.OUTPUT_DIR):
        os.makedirs(args.OUTPUT_DIR)

    if os.path.exists(args.INPUT_DIR) and os.path.isdir(args.INPUT_DIR):
        main(args.INPUT_DIR, args.OUTPUT_DIR)
    else:
        logger.error("Supplied input directory does not exist or is not "
                     "a directory")
        sys.exit(1)
