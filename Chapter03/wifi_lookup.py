from __future__ import print_function
import argparse
import csv
import os
import sys
import xml.etree.ElementTree as ET
import requests

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
__description__ = "Wifi MAC Address lookup utility"


def main(in_file, out_csv, type, api_key):
    if type == 'xml':
        wifi = parse_xml(in_file)
    else:
        wifi = parse_txt(in_file)

    query_wigle(wifi, out_csv, api_key)


def parse_xml(xml_file):
    wifi = {}
    xmlns = "{http://pa.cellebrite.com/report/2.0}"
    print("[+] Opening {} report".format(xml_file))
    xml_tree = ET.parse(xml_file)
    print("[+] Parsing report for all connected WiFi addresses")
    root = xml_tree.getroot()
    for child in root.iter():
        if child.tag == xmlns + "model":
            if child.get("type") == "Location":
                for field in child.findall(xmlns + "field"):
                    if field.get("name") == "TimeStamp":
                        ts_value = field.find(xmlns + "value")
                        try:
                            ts = ts_value.text
                        except AttributeError:
                            continue
                    if field.get("name") == "Description":
                        value = field.find(xmlns + "value")
                        try:
                            value_text = value.text
                        except AttributeError:
                            continue
                        if "SSID" in value.text:
                            bssid, ssid = value.text.split("\t")
                            bssid = bssid[7:]
                            ssid = ssid[6:]
                            if bssid in wifi.keys():
                                wifi[bssid]["Timestamps"].append(ts)
                                wifi[bssid]["SSID"].append(ssid)
                            else:
                                wifi[bssid] = {
                                    "Timestamps": [ts], "SSID": [ssid],
                                    "Wigle": {}}
    return wifi


def parse_txt(txt_file):
    wifi = {}
    print("[+] Extracting MAC addresses from {}".format(txt_file))
    with open(txt_file) as mac_file:
        for line in mac_file:
            wifi[line.strip()] = {"Timestamps": ["N/A"], "SSID": ["N/A"],
                                  "Wigle": {}}
    return wifi


def query_mac_addr(mac_addr, api_key):
    query_url = "https://api.wigle.net/api/v2/network/search?" \
        "onlymine=false&freenet=false&paynet=false" \
        "&netid={}".format(mac_addr)
    req = requests.get(query_url, auth=(api_key[0], api_key[1]))
    return req.json()


def query_wigle(wifi_dictionary, out_csv, api_key):
    print("[+] Querying Wigle.net through Python API for {} "
          "APs".format(len(wifi_dictionary)))
    for mac in wifi_dictionary:
        wigle_results = query_mac_addr(mac, api_key)
        try:
            if wigle_results["resultCount"] == 0:
                wifi_dictionary[mac]["Wigle"]["results"] = []
                continue
            else:
                wifi_dictionary[mac]["Wigle"] = wigle_results
        except KeyError:
            if wigle_results["error"] == "too many queries today":
                print("[-] Wigle daily query limit exceeded")
                wifi_dictionary[mac]["Wigle"]["results"] = []
                continue
            else:
                print("[-] Other error encountered for "
                      "address {}: {}".format(mac, wigle_results['error']))
                wifi_dictionary[mac]["Wigle"]["results"] = []
                continue
    prep_output(out_csv, wifi_dictionary)


def prep_output(output, data):
    csv_data = {}
    google_map = "https://www.google.com/maps/search/"
    for x, mac in enumerate(data):
        for y, ts in enumerate(data[mac]["Timestamps"]):
            for z, result in enumerate(data[mac]["Wigle"]["results"]):
                shortres = data[mac]["Wigle"]["results"][z]
                g_map_url = "{}{},{}".format(
                    google_map, shortres["trilat"], shortres["trilong"])
                csv_data["{}-{}-{}".format(x, y, z)] = {
                    **{
                        "BSSID": mac, "SSID": data[mac]["SSID"][y],
                        "Cellebrite Connection Time": ts,
                        "Google Map URL": g_map_url},
                    **shortres
                }

    write_csv(output, csv_data)


def write_csv(output, data):
    print("[+] Writing data to {}".format(output))
    field_list = set()
    for row in data:
        for field in data[row]:
            field_list.add(field)

    with open(output, "w", newline="") as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=sorted(
            field_list), extrasaction='ignore')
        csv_writer.writeheader()
        for csv_row in data:
            csv_writer.writerow(data[csv_row])


if __name__ == "__main__":
    # Command-line Argument Parser
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("INPUT_FILE", help="INPUT FILE with MAC Addresses")
    parser.add_argument("OUTPUT_CSV", help="Output CSV File")
    parser.add_argument(
        "-t", help="Input type: Cellebrite XML report or TXT file",
        choices=('xml', 'txt'), default="xml")
    parser.add_argument('--api', help="Path to API key file",
                        default=os.path.expanduser("~/.wigle_api"),
                        type=argparse.FileType('r'))
    args = parser.parse_args()

    if not os.path.exists(args.INPUT_FILE) or \
            not os.path.isfile(args.INPUT_FILE):
        print("[-] {} does not exist or is not a file".format(
            args.INPUT_FILE))
        sys.exit(1)

    directory = os.path.dirname(args.OUTPUT_CSV)
    if directory != '' and not os.path.exists(directory):
        os.makedirs(directory)

    api_key = args.api.readline().strip().split(":")

    main(args.INPUT_FILE, args.OUTPUT_CSV, args.t, api_key)
