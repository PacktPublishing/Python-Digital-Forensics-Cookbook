from __future__ import print_function
import argparse
import csv
from datetime import datetime
import os
import pytsk3
import pyewf
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
__description__ = "Utility to iterate over files in an evidence containers"


def main(image, img_type, output, part_type):
    volume = None
    print("[+] Opening {}".format(image))
    if img_type == "ewf":
        try:
            filenames = pyewf.glob(image)
        except IOError:
            _, e, _ = sys.exc_info()
            print("[-] Invalid EWF format:\n {}".format(e))
            sys.exit(2)

        ewf_handle = pyewf.handle()
        ewf_handle.open(filenames)

        # Open PYTSK3 handle on EWF Image
        img_info = EWFImgInfo(ewf_handle)
    else:
        img_info = pytsk3.Img_Info(image)

    try:
        if part_type is not None:
            attr_id = getattr(pytsk3, "TSK_VS_TYPE_" + part_type)
            volume = pytsk3.Volume_Info(img_info, attr_id)
        else:
            volume = pytsk3.Volume_Info(img_info)
    except IOError:
        _, e, _ = sys.exc_info()
        print("[-] Unable to read partition table:\n {}".format(e))

    open_fs(volume, img_info, output)


def open_fs(vol, img, output):
    print("[+] Recursing through files..")
    recursed_data = []
    # Open FS and Recurse
    if vol is not None:
        for part in vol:
            if part.len > 2048 and "Unallocated" not in part.desc and \
                    "Extended" not in part.desc and \
                    "Primary Table" not in part.desc:
                try:
                    fs = pytsk3.FS_Info(
                        img, offset=part.start * vol.info.block_size)
                except IOError:
                    _, e, _ = sys.exc_info()
                    print("[-] Unable to open FS:\n {}".format(e))
                root = fs.open_dir(path="/")
                data = recurse_files(part.addr, fs, root, [], [], [""])
                recursed_data.append(data)

    else:
        try:
            fs = pytsk3.FS_Info(img)
        except IOError:
            _, e, _ = sys.exc_info()
            print("[-] Unable to open FS:\n {}".format(e))
        root = fs.open_dir(path="/")
        data = recurse_files(1, fs, root, [], [], [""])
        recursed_data.append(data)
    write_csv(recursed_data, output)


def recurse_files(part, fs, root_dir, dirs, data, parent):
    dirs.append(root_dir.info.fs_file.meta.addr)
    for fs_object in root_dir:
        # Skip ".", ".." or directory entries without a name.
        if not hasattr(fs_object, "info") or \
                not hasattr(fs_object.info, "name") or \
                not hasattr(fs_object.info.name, "name") or \
                fs_object.info.name.name in [".", ".."]:
            continue
        try:
            file_name = fs_object.info.name.name
            file_path = "{}/{}".format(
                "/".join(parent), fs_object.info.name.name)
            try:
                if fs_object.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                    f_type = "DIR"
                    file_ext = ""
                else:
                    f_type = "FILE"
                    if "." in file_name:
                        file_ext = file_name.rsplit(".")[-1].lower()
                    else:
                        file_ext = ""
            except AttributeError:
                continue

            size = fs_object.info.meta.size
            create = convert_time(fs_object.info.meta.crtime)
            change = convert_time(fs_object.info.meta.ctime)
            modify = convert_time(fs_object.info.meta.mtime)
            data.append(["PARTITION {}".format(part), file_name, file_ext,
                         f_type, create, change, modify, size, file_path])

            if f_type == "DIR":
                parent.append(fs_object.info.name.name)
                sub_directory = fs_object.as_directory()
                inode = fs_object.info.meta.addr

                # This ensures that we don't recurse into a directory
                # above the current level and thus avoid circular loops.
                if inode not in dirs:
                    recurse_files(part, fs, sub_directory, dirs, data,
                                  parent)
                parent.pop(-1)

        except IOError:
            pass
    dirs.pop(-1)
    return data


def write_csv(data, output):
    if data == []:
        print("[-] No output results to write")
        sys.exit(3)

    print("[+] Writing output to {}".format(output))
    with open(output, "wb") as csvfile:
        csv_writer = csv.writer(csvfile)
        headers = ["Partition", "File", "File Ext", "File Type",
                   "Create Date", "Modify Date", "Change Date", "Size",
                   "File Path"]
        csv_writer.writerow(headers)
        for result_list in data:
            csv_writer.writerows(result_list)


def convert_time(ts):
    if str(ts) == "0":
        return ""
    return datetime.utcfromtimestamp(ts)


class EWFImgInfo(pytsk3.Img_Info):
    def __init__(self, ewf_handle):
        self._ewf_handle = ewf_handle
        super(EWFImgInfo, self).__init__(url="",
                                         type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

    def close(self):
        self._ewf_handle.close()

    def read(self, offset, size):
        self._ewf_handle.seek(offset)
        return self._ewf_handle.read(size)

    def get_size(self):
        return self._ewf_handle.get_media_size()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("EVIDENCE_FILE", help="Evidence file path")
    parser.add_argument("TYPE", help="Type of Evidence",
                        choices=("raw", "ewf"))
    parser.add_argument("OUTPUT_CSV", help="Output CSV with lookup results")
    parser.add_argument("-p", help="Partition Type",
                        choices=("DOS", "GPT", "MAC", "SUN"))
    args = parser.parse_args()

    directory = os.path.dirname(args.OUTPUT_CSV)
    if not os.path.exists(directory) and directory != "":
        os.makedirs(directory)

    if os.path.exists(args.EVIDENCE_FILE) and os.path.isfile(args.EVIDENCE_FILE):
        main(args.EVIDENCE_FILE, args.TYPE, args.OUTPUT_CSV, args.p)
    else:
        print("[-] Supplied input file {} does not exist or is not a "
              "file".format(args.EVIDENCE_FILE))
        sys.exit(1)
