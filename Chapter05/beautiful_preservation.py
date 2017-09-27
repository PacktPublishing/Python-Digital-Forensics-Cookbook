from __future__ import print_function
import argparse
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
import hashlib
import logging
import os
import ssl
import sys
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
__description__ = "BeautifulSoup Website Preservation Tool"

logger = logging.getLogger(__name__)


def main(website, output_dir):
    base_name = website.replace(
        "https://", "").replace("http://", "").replace("www.", "")
    link_queue = set()
    if "http://" not in website and "https://" not in website:
        logger.error(
            "Exiting preservation - invalid user input: {}".format(
                website))
        sys.exit(1)
    logger.info("Accessing {} webpage".format(website))
    context = ssl._create_unverified_context()

    try:
        index = urlopen(website, context=context).read().decode("utf-8")
    except urllib.error.HTTPError as e:
        logger.error(
            "Exiting preservation - unable to access page: {}".format(
                website))
        sys.exit(2)
    logger.debug("Successfully accessed {}".format(website))
    write_output(website, index, output_dir)
    link_queue = find_links(base_name, index, link_queue)
    logger.info("Found {} initial links on webpage".format(
        len(link_queue)))
    recurse_pages(website, link_queue, context, output_dir)
    logger.info("Completed preservation of {}".format(website))


def find_links(website, page, queue):
    for link in BeautifulSoup(page, "html.parser",
                              parse_only=SoupStrainer("a", href=True)):
        if website in link.get("href"):
            if not os.path.basename(link.get("href")).startswith("#"):
                queue.add(link.get("href"))
    return queue


def recurse_pages(website, queue, context, output_dir):
    processed = []
    counter = 0
    while True:
        counter += 1
        if len(processed) == len(queue):
            break
        for link in queue.copy():
            if link in processed:
                continue
            processed.append(link)
            try:
                page = urlopen(link, context=context).read().decode(
                    "utf-8")
            except urllib.error.HTTPError as e:
                msg = "Error accessing webpage: {}".format(link)
                logger.error(msg)
                continue
            write_output(link, page, output_dir, counter)
            queue = find_links(website, page, queue)
    logger.info("Identified {} links throughout website".format(
        len(queue)))


def hash_data(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode("utf-8"))
    return sha256.hexdigest()


def hash_file(file):
    sha256 = hashlib.sha256()
    with open(file, "rb") as in_file:
        sha256.update(in_file.read())
    return sha256.hexdigest()


def write_output(name, data, output_dir, counter=0):
    name = name.replace("http://", "").replace("https://", "").rstrip("//")
    directory = os.path.join(output_dir, os.path.dirname(name))
    if not os.path.exists(directory) and os.path.dirname(name) != "":
        os.makedirs(directory)

    logger.debug("Writing {} to {}".format(name, output_dir))
    logger.debug("Data Hash: {}".format(hash_data(data)))
    path = os.path.join(output_dir, name)
    path = path + "_" + str(counter)
    with open(path, "w") as outfile:
        outfile.write(data)
    logger.debug("Output File Hash: {}".format(hash_file(path)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("DOMAIN", help="Website Domain")
    parser.add_argument("OUTPUT_DIR", help="Preservation Output Directory")
    parser.add_argument("-l", help="Log file path",
                        default=__file__[:-3] + ".log")
    args = parser.parse_args()

    logger.setLevel(logging.DEBUG)
    msg_fmt = logging.Formatter("%(asctime)-15s %(funcName)-10s"
                                "%(levelname)-8s %(message)s")
    strhndl = logging.StreamHandler(sys.stderr)
    strhndl.setFormatter(fmt=msg_fmt)
    fhndl = logging.FileHandler(args.l, mode='a')
    fhndl.setFormatter(fmt=msg_fmt)

    logger.addHandler(strhndl)
    logger.addHandler(fhndl)

    logger.info("Starting BS Preservation")
    logger.debug("Supplied arguments: {}".format(sys.argv[1:]))
    logger.debug("System " + sys.platform)
    logger.debug("Version " + sys.version)

    if not os.path.exists(args.OUTPUT_DIR):
        os.makedirs(args.OUTPUT_DIR)

    main(args.DOMAIN, args.OUTPUT_DIR)
