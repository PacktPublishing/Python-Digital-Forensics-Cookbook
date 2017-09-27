from __future__ import print_function
import argparse
import biplist
import os
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
__description__ = "Property List Parser"


def main(plist):
    print("[+] Opening {} file".format(plist))
    try:
        plist_data = biplist.readPlist(plist)
    except (biplist.InvalidPlistException,
            biplist.NotBinaryPlistException) as e:
        print("[-] Invalid PLIST file - unable to be opened by biplist")
        sys.exit(2)

    print("[+] Printing Info.plist Device "
          "and User Information to Console\n")
    for k in plist_data:
        if k != 'Applications' and k != 'iTunes Files':
            print("{:<25s} - {}".format(k, plist_data[k]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("PLIST_FILE", help="Input PList File")
    args = parser.parse_args()

    if not os.path.exists(args.PLIST_FILE) or \
            not os.path.isfile(args.PLIST_FILE):
        print("[-] {} does not exist or is not a file".format(
            args.PLIST_FILE))
        sys.exit(1)

    main(args.PLIST_FILE)
