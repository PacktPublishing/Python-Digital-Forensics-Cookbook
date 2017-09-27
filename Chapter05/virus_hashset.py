from __future__ import print_function
import argparse
import os
import ssl
import sys
import tqdm
from urllib.request import urlopen
import urllib.error

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
__description__ = "Utility to download and generate hashlists for malware"


def main(hashset, **kwargs):
    url = "https://virusshare.com/hashes.4n6"
    print("[+] Identifying hash set range from {}".format(url))
    context = ssl._create_unverified_context()

    try:
        index = urlopen(url, context=context).read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print("[-] Error accessing webpage - exiting..")
        sys.exit(1)
    tag = index.rfind(r'<a href="hashes/VirusShare_')
    stop = int(index[tag + 27: tag + 27 + 5].lstrip("0"))

    if "start" not in kwargs:
        start = 0
    else:
        start = kwargs["start"]

    if start < 0 or start > stop:
        print("[-] Supplied start argument must be greater than or equal "
              "to zero but less than the latest hash list, "
              "currently: {}".format(stop))
        sys.exit(2)

    print("[+] Creating a hashset from hash lists {} to {}".format(
        start, stop))
    hashes_downloaded = 0
    for x in tqdm.trange(start, stop + 1, unit_scale=True,
                         desc="Progress"):
        url_hash = "https://virusshare.com/hashes/VirusShare_"\
                   "{}.md5".format(str(x).zfill(5))
        try:
            hashes = urlopen(
                url_hash, context=context).read().decode("utf-8")
            hashes_list = hashes.split("\n")
        except urllib.error.HTTPError as e:
            print("[-] Error accessing webpage for hash list {}"
                  " - continuing..".format(x))
            continue

        with open(hashset, "a+") as hashfile:
            for line in hashes_list:
                if not line.startswith("#") and line != "":
                    hashes_downloaded += 1
                    hashfile.write(line + '\n')

    print("[+] Finished downloading {} hashes into {}".format(
        hashes_downloaded, hashset))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("OUTPUT_HASH", help="Output Hashset")
    parser.add_argument("--start", type=int,
                        help="Optional starting location")
    args = parser.parse_args()

    directory = os.path.dirname(args.OUTPUT_HASH)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if args.start:
        main(args.OUTPUT_HASH, start=args.start)
    else:
        main(args.OUTPUT_HASH)
