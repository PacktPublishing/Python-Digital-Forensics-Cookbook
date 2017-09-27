from __future__ import print_function
import argparse
import csv
import hashlib
import json
import os
import requests
import sys
import time

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
__description__ = "Utility to review malicious websites or files with VT"


def main(input_file, output, api, limit, type):
    objects = set()
    with open(input_file) as infile:
        for line in infile:
            if line.strip() != "":
                objects.add(line.strip())
    if type == "domain":
        data = query_domain(objects, api, limit)
    else:
        data = query_file(objects, api, limit)
    write_csv(data, output)


def query_domain(domains, api, limit):
    if not os.path.exists(api) and os.path.isfile(api):
        print("[-] API key file {} does not exist or is not a file".format(
            api))
        sys.exit(2)

    with open(api) as infile:
        api = infile.read().strip()
    json_data = []

    print("[+] Querying {} Domains / IPs using VirusTotal API".format(
        len(domains)))
    count = 0
    for domain in domains:
        count += 1
        params = {"resource": domain, "apikey": api, "scan": 1}
        response = requests.post(
            'https://www.virustotal.com/vtapi/v2/url/report',
            params=params)
        json_response = response.json()
        if "Scan finished" in json_response["verbose_msg"]:
            json_data.append(json_response)

        if limit and count == 3:
            print("[+] Halting execution for a minute to comply with "
                  "public API key restrictions")
            time.sleep(60)
            print("[+] Continuing execution of remaining Domains / IPs")
            count = 0

    return json_data


def query_file(files, api, limit):
    if not os.path.exists(api) and os.path.isfile(api):
        print("[-] API key file {} does not exist or is not a file".format(
            api))
        sys.exit(3)

    with open(api) as infile:
        api = infile.read().strip()
    json_data = []

    print("[+] Hashing and Querying {} Files using VirusTotal API".format(
        len(files)))
    count = 0
    for file_entry in files:
        if os.path.exists(file_entry):
            file_hash = hash_file(file_entry)
        elif len(file_entry) == 32:
            file_hash = file_entry
        else:
            continue
        count += 1
        params = {"resource": file_hash, "apikey": api}
        response = requests.post(
            'https://www.virustotal.com/vtapi/v2/file/report',
            params=params)
        json_response = response.json()
        if "Scan finished" in json_response["verbose_msg"]:
            json_data.append(json_response)

        if limit and count == 3:
            print("[+] Halting execution for a minute to comply with "
                  "public API key restrictions")
            time.sleep(60)
            print("[+] Continuing execution of remaining files")
            count = 0

    return json_data


def hash_file(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as open_file:
        buff_size = 1024
        buff = open_file.read(buff_size)

        while buff:
            sha256.update(buff)
            buff = open_file.read(buff_size)
    return sha256.hexdigest()


def write_csv(data, output):
    if data == []:
        print("[-] No output results to write")
        sys.exit(4)

    print("[+] Writing output for {} domains with results to {}".format(
        len(data), output))
    flatten_data = []
    field_list = ["URL", "Scan Date", "Service",
                  "Detected", "Result", "VirusTotal Link"]
    for result in data:
        for service in result["scans"]:
            flatten_data.append(
                {"URL": result.get("url", ""),
                 "Scan Date": result.get("scan_date", ""),
                 "VirusTotal Link": result.get("permalink", ""),
                 "Service": service,
                 "Detected": result["scans"][service]["detected"],
                 "Result": result["scans"][service]["result"]})

    with open(output, "w", newline="") as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=field_list)
        csv_writer.writeheader()
        for result in flatten_data:
            csv_writer.writerow(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("INPUT_FILE",
                        help="Text File containing list of file paths/"
                             "hashes or domains/IPs")
    parser.add_argument("OUTPUT_CSV",
                        help="Output CSV with lookup results")
    parser.add_argument("API_KEY", help="Text File containing API key")
    parser.add_argument("-t", "--type",
                        help="Type of data: file or domain",
                        choices=("file", "domain"), default="domain")
    parser.add_argument(
        "--limit", action="store_true",
        help="Limit requests to comply with public API key restrictions")
    args = parser.parse_args()

    directory = os.path.dirname(args.OUTPUT_CSV)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if os.path.exists(args.INPUT_FILE) and os.path.isfile(args.INPUT_FILE):
        main(args.INPUT_FILE, args.OUTPUT_CSV,
             args.API_KEY, args.limit, args.type)
    else:
        print("[-] Supplied input file {} does not exist or is not a "
              "file".format(args.INPUT_FILE))
        sys.exit(1)
