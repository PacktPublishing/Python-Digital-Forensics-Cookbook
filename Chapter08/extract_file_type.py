from __future__ import print_function
import argparse
import csv
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
__description__ = "Utility to extract files from evidence containers"


def main(image, img_type, ext, output, part_type):
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

    open_fs(volume, img_info, ext, output)


def open_fs(vol, img, ext, output):
    # Open FS and Recurse
    print("[+] Recursing through files and writing file extension matches "
          "to output directory")
    if vol is not None:
        for part in vol:
            if part.len > 2048 and "Unallocated" not in part.desc \
                    and "Extended" not in part.desc \
                    and "Primary Table" not in part.desc:
                try:
                    fs = pytsk3.FS_Info(
                        img, offset=part.start * vol.info.block_size)
                except IOError:
                    _, e, _ = sys.exc_info()
                    print("[-] Unable to open FS:\n {}".format(e))
                root = fs.open_dir(path="/")
                recurse_files(part.addr, fs, root, [], [""], ext, output)

    else:
        try:
            fs = pytsk3.FS_Info(img)
        except IOError:
            _, e, _ = sys.exc_info()
            print("[-] Unable to open FS:\n {}".format(e))
        root = fs.open_dir(path="/")
        recurse_files(1, fs, root, [], [""], ext, output)


def recurse_files(part, fs, root_dir, dirs, parent, ext, output):
    extensions = [x.strip().lower() for x in ext.split(',')]
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
            file_path = "{}/{}".format("/".join(parent),
                                       fs_object.info.name.name)
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

            if file_ext.strip() in extensions:
                print("{}".format(file_path))
                file_writer(fs_object, file_name, file_ext, file_path,
                            output)

            if f_type == "DIR":
                parent.append(fs_object.info.name.name)
                sub_directory = fs_object.as_directory()
                inode = fs_object.info.meta.addr
                if inode not in dirs:
                    recurse_files(part, fs, sub_directory, dirs,
                                  parent, ext, output)
                    parent.pop(-1)

        except IOError:
            pass
    dirs.pop(-1)


def file_writer(fs_object, name, ext, path, output):
    output_dir = os.path.join(output, ext,
                              os.path.dirname(path.lstrip("//")))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, name), "w") as outfile:
        outfile.write(fs_object.read_random(0, fs_object.info.meta.size))


class EWFImgInfo(pytsk3.Img_Info):
        def __init__(self, ewf_handle):
            self._ewf_handle = ewf_handle
            super(EWFImgInfo, self).__init__(
                url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)

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
    parser.add_argument("EXT",
                        help="Comma-delimited file extensions to extract")
    parser.add_argument("OUTPUT_DIR", help="Output Directory")
    parser.add_argument("-p", help="Partition Type",
                        choices=("DOS", "GPT", "MAC", "SUN"))
    args = parser.parse_args()

    if not os.path.exists(args.OUTPUT_DIR):
        os.makedirs(args.OUTPUT_DIR)

    if os.path.exists(args.EVIDENCE_FILE) and \
            os.path.isfile(args.EVIDENCE_FILE):
        main(args.EVIDENCE_FILE, args.TYPE, args.EXT, args.OUTPUT_DIR,
             args.p)
    else:
        print("[-] Supplied input file {} does not exist or is not a "
              "file".format(args.EVIDENCE_FILE))
        sys.exit(1)
