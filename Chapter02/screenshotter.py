from __future__ import print_function
import argparse
from multiprocessing import freeze_support
import os
import sys
import time

try:
    import pyscreenshot
    import wx
except ImportError:
    print("[-] Install wx and pyscreenshot to use this script")
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
__description__ = "Capture incremental screenshots"


def main(output_dir, interval, total):
    i = 0
    while True:
        i += 1
        time.sleep(interval)
        image = pyscreenshot.grab()
        output = os.path.join(output_dir, "screenshot_{}.png").format(i)
        image.save(output)
        print("[+] Took screenshot {} and saved it to {}".format(
            i, output_dir))
        if total is not None and i == total:
            print("[+] Finished taking {} screenshots every {} "
                  "seconds".format(total, interval))
            sys.exit(0)


if __name__ == "__main__":
    # Command-line Argument Parser
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("OUTPUT_DIR", help="Desired Output Path")
    parser.add_argument(
        "INTERVAL", help="Screenshot interval (seconds)", type=int)
    parser.add_argument(
        "-total", help="Total number of screenshots to take", type=int)
    args = parser.parse_args()

    if not os.path.exists(args.OUTPUT_DIR):
        os.makedirs(args.OUTPUT_DIR)

    main(args.OUTPUT_DIR, args.INTERVAL, args.total)
