from __future__ import print_function
from argparse import ArgumentParser, FileType
import datetime
from PyPDF2 import PdfFileReader
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
__description__ = "Utility to extract metadata from PDF files"

parser = ArgumentParser(
    description=__description__,
    epilog="Developed by {} on {}".format(", ".join(__authors__), __date__)
)
parser.add_argument('PDF_FILE', help='Path to PDF file',
                    type=FileType('rb'))
args = parser.parse_args()

pdf_file = PdfFileReader(args.PDF_FILE)

xmpm = pdf_file.getXmpMetadata()
if xmpm is None:
    print("No XMP metadata found in document.")
    sys.exit()


def custom_print(fmt_str, value):
    if isinstance(value, list):
        print(fmt_str.format(", ".join(value)))
    elif isinstance(value, dict):
        fmt_value = [":".join((k, v)) for k, v in value.items()]
        print(fmt_str.format(", ".join(value)))
    elif isinstance(value, str) or isinstance(value, bool):
        print(fmt_str.format(value))
    elif isinstance(value, bytes):
        print(fmt_str.format(value.decode()))
    elif isinstance(value, datetime.datetime):
        print(fmt_str.format(value.isoformat()))
    elif value is None:
        print(fmt_str.format("N/A"))
    else:
        print("warn: unhandled type {} found".format(type(value)))


# Definitions from
# http://wwwimages.adobe.com/content/dam/Adobe/en/devnet/xmp/pdfs/XMP%20SDK%20Release%20cc-2016-08/XMPSpecificationPart1.pdf
custom_print("Title: {}", xmpm.dc_title)
custom_print("Creator(s): {}", xmpm.dc_creator)
custom_print("Contributors: {}", xmpm.dc_contributor)
custom_print("Subject: {}", xmpm.dc_subject)
custom_print("Description: {}", xmpm.dc_description)
custom_print("Created: {}", xmpm.xmp_createDate)
custom_print("Modified: {}", xmpm.xmp_modifyDate)
custom_print("Event Dates: {}", xmpm.dc_date)
custom_print("Created With: {}", xmpm.xmp_creatorTool)
custom_print("Document ID: {}", xmpm.xmpmm_documentId)
custom_print("Instance ID: {}", xmpm.xmpmm_instanceId)
custom_print("Language: {}", xmpm.dc_language)
custom_print("Publisher: {}", xmpm.dc_publisher)
custom_print("Resource Type: {}", xmpm.dc_format)
custom_print("Type: {}", xmpm.dc_type)

if xmpm.custom_properties:
    print("Custom Properties:")
    for k, v in xmpm.custom_properties.items():
        print("\t{}: {}".format(k, v))
