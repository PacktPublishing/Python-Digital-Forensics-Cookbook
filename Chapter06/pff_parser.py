from __future__ import print_function
from argparse import ArgumentParser
import csv
import pypff
import re

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
__description__ = "Utility to read content and metadata from PSTs and OSTs"


def process_folders(pff_folder):
    folder_name = pff_folder.name if pff_folder.name else "N/A"
    print("Folder: {} (sub-dir: {}/sub-msg: {})".format(folder_name,
          pff_folder.number_of_sub_folders,
          pff_folder.number_of_sub_messages))

    # Process messages within a folder
    data_list = []
    for msg in pff_folder.sub_messages:
        data_dict = process_message(msg)
        data_dict['folder'] = folder_name
        data_list.append(data_dict)

    # Process folders within a folder
    for folder in pff_folder.sub_folders:
        data_list += process_folders(folder)

    return data_list


def process_message(msg):
    # Extract attributes
    attribs = ['conversation_topic', 'number_of_attachments',
               'sender_name', 'subject']
    data_dict = {}
    for attrib in attribs:
        data_dict[attrib] = getattr(msg, attrib, "N/A")

    if msg.transport_headers is not None:
        data_dict.update(process_headers(msg.transport_headers))

    return data_dict


def process_headers(header):
    # Read and process header information
    key_pattern = re.compile("^([A-Za-z\-]+:)(.*)$")
    header_data = {}
    for line in header.split("\r\n"):
        if len(line) == 0:
            continue

        reg_result = key_pattern.match(line)
        if reg_result:
            key = reg_result.group(1).strip(":").strip()
            value = reg_result.group(2).strip()
        else:
            value = line

        if key.lower() in header_data:
            if isinstance(header_data[key.lower()], list):
                header_data[key.lower()].append(value)
            else:
                header_data[key.lower()] = [header_data[key.lower()],
                                            value]
        else:
            header_data[key.lower()] = value
    return header_data


def write_data(outfile, data_list):
    # Build out additional columns
    print("Writing Report: ", outfile)
    columns = ['folder', 'conversation_topic', 'number_of_attachments',
               'sender_name', 'subject']
    formatted_data_list = []
    for entry in data_list:
        tmp_entry = {}

        for k, v in entry.items():
            if k not in columns:
                columns.append(k)

            if isinstance(v, list):
                tmp_entry[k] = ", ".join(v)
            else:
                tmp_entry[k] = v
        formatted_data_list.append(tmp_entry)

    # Write CSV report
    with open(outfile, 'wb') as openfile:
        csvfile = csv.DictWriter(openfile, columns)
        csvfile.writeheader()
        csvfile.writerows(formatted_data_list)


if __name__ == '__main__':
    parser = ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("PFF_FILE", help="Path to PST or OST File")
    parser.add_argument("CSV_REPORT", help="Path to CSV report location")
    args = parser.parse_args()

    # Open file
    pff_obj = pypff.file()
    pff_obj.open(args.PFF_FILE)

    # Parse and close file
    parsed_data = process_folders(pff_obj.root_folder)
    pff_obj.close()

    # Write CSV report
    write_data(args.CSV_REPORT, parsed_data)
