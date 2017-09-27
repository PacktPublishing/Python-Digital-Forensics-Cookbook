from __future__ import print_function
from argparse import ArgumentParser
import mailbox
import os
import time
import csv
from tqdm import tqdm
import base64

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
__description__ = "Utility to parse the MBOX mail file format"


def custom_reader(data_stream):
    data = data_stream.read()
    try:
        content = data.decode("ascii")
    except (UnicodeDecodeError, UnicodeEncodeError) as e:
        content = data.decode("cp1252", errors="replace")
    return mailbox.mboxMessage(content)


def get_filename(msg):
    if 'name=' in msg.get("Content-Disposition", "N/A"):
        fname_data = msg["Content-Disposition"].replace("\r\n", " ")
        fname = [x for x in fname_data.split("; ") if 'name=' in x]
        file_name = fname[0].split("=", 1)[-1]

    elif 'name=' in msg.get("Content-Type", "N/A"):
        fname_data = msg["Content-Type"].replace("\r\n", " ")
        fname = [x for x in fname_data.split("; ") if 'name=' in x]
        file_name = fname[0].split("=", 1)[-1]

    else:
        file_name = "NO_FILENAME"

    fchars = [x for x in file_name if x.isalnum() or x.isspace() or
              x == "."]
    return "".join(fchars)


def export_content(msg, out_dir, content_data):
    file_name = get_filename(msg)
    file_ext = "FILE"
    if "." in file_name:
        file_ext = file_name.rsplit(".", 1)[-1]

    file_name = "{}_{:.4f}.{}".format(
        file_name.rsplit(".", 1)[0], time.time(), file_ext)
    file_name = os.path.join(out_dir, file_name)

    if isinstance(content_data, str):
        open(file_name, 'w').write(content_data)
    else:
        open(file_name, 'wb').write(content_data)

    return file_name


def write_payload(msg, out_dir):
    pyld = msg.get_payload()
    export_path = []
    if msg.is_multipart():
        for entry in pyld:
            export_path += write_payload(entry, out_dir)

    else:
        content_type = msg.get_content_type()
        if "application/" in content_type.lower():
            content = base64.b64decode(msg.get_payload())
            export_path.append(export_content(msg, out_dir, content))
        elif "image/" in content_type.lower():
            content = base64.b64decode(msg.get_payload())
            export_path.append(export_content(msg, out_dir, content))
        elif "video/" in content_type.lower():
            content = base64.b64decode(msg.get_payload())
            export_path.append(export_content(msg, out_dir, content))
        elif "audio/" in content_type.lower():
            content = base64.b64decode(msg.get_payload())
            export_path.append(export_content(msg, out_dir, content))
        elif "text/csv" in content_type.lower():
            content = base64.b64decode(msg.get_payload())
            export_path.append(export_content(msg, out_dir, content))
        elif "info/" in content_type.lower():
            export_path.append(export_content(msg, out_dir,
                                              msg.get_payload()))
        elif "text/calendar" in content_type.lower():
            export_path.append(export_content(msg, out_dir,
                                              msg.get_payload()))
        elif "text/rtf" in content_type.lower():
            export_path.append(export_content(msg, out_dir,
                                              msg.get_payload()))
        else:
            if "name=" in msg.get('Content-Disposition', "N/A"):
                content = base64.b64decode(msg.get_payload())
                export_path.append(export_content(msg, out_dir, content))
            elif "name=" in msg.get('Content-Type', "N/A"):
                content = base64.b64decode(msg.get_payload())
                export_path.append(export_content(msg, out_dir, content))

    return export_path


def create_report(output_data, output_file, columns):
    with open(output_file, 'w', newline="") as outfile:
        csvfile = csv.DictWriter(outfile, columns)
        csvfile.writeheader()
        csvfile.writerows(output_data)


def main(mbox_file, output_dir):
    # Read in the MBOX File
    print("Reading mbox file...")
    mbox = mailbox.mbox(mbox_file, factory=custom_reader)
    print("{} messages to parse".format(len(mbox)))

    # Prep for loop
    parsed_data = []
    attachments_dir = os.path.join(output_dir, "attachments")
    if not os.path.exists(attachments_dir):
        os.makedirs(attachments_dir)
    columns = ["Date", "From", "To", "Subject", "X-Gmail-Labels",
               "Return-Path", "Received", "Content-Type", "Message-ID",
               "X-GM-THRID", "num_attachments_exported", "export_path"]

    # Iterate through mbox with progressbar
    for message in tqdm(mbox):
        # Preserve header information
        msg_data = dict()
        header_data = dict(message._headers)
        for hdr in columns:
            msg_data[hdr] = header_data.get(hdr, "N/A")

        # Extract attachments
        if len(message.get_payload()):
            export_path = write_payload(message, attachments_dir)
            msg_data['num_attachments_exported'] = len(export_path)
            msg_data['export_path'] = ", ".join(export_path)

        parsed_data.append(msg_data)

    # Create CSV report
    create_report(
        parsed_data, os.path.join(output_dir, "mbox_report.csv"), columns
    )


if __name__ == '__main__':
    parser = ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("MBOX", help="Path to mbox file")
    parser.add_argument("OUTPUT_DIR",
                        help="Path to output directory to write report "
                        "and exported content")
    args = parser.parse_args()

    main(args.MBOX, args.OUTPUT_DIR)
