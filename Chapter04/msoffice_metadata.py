from __future__ import print_function
from argparse import ArgumentParser
from datetime import datetime as dt
from xml.etree import ElementTree as etree
import zipfile

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
__description__ = "Read metadta from Office files"

parser = argparse.ArgumentParser(
    description=__description__,
    epilog="Developed by {} on {}".format(", ".join(__authors__), __date__)
)
parser.add_argument("Office_File", help="Path to office file to read")
args = parser.parse_args()

# Check if input file is a zipfile
zipfile.is_zipfile(args.Office_File)

# Open the file (MS Office 2007 or later)
zfile = zipfile.ZipFile(args.Office_File)

# Extract key elements for processing
core_xml = etree.fromstring(zfile.read('docProps/core.xml'))
app_xml = etree.fromstring(zfile.read('docProps/app.xml'))

# Core.xml tag mapping
core_mapping = {
    'title': 'Title',
    'subject': 'Subject',
    'creator': 'Author(s)',
    'keywords': 'Keywords',
    'description': 'Description',
    'lastModifiedBy': 'Last Modified By',
    'modified': 'Modified Date',
    'created': 'Created Date',
    'category': 'Category',
    'contentStatus': 'Status',
    'revision': 'Revision'
}

for element in core_xml.getchildren():
    for key, title in core_mapping.items():
        if key in element.tag:
            if 'date' in title.lower():
                text = dt.strptime(element.text, "%Y-%m-%dT%H:%M:%SZ")
            else:
                text = element.text
            print("{}: {}".format(title, text))

app_mapping = {
    'TotalTime': 'Edit Time (minutes)',
    'Pages': 'Page Count',
    'Words': 'Word Count',
    'Characters': 'Character Count',
    'Lines': 'Line Count',
    'Paragraphs': 'Paragraph Count',
    'Company': 'Company',
    'HyperlinkBase': 'Hyperlink Base',
    'Slides': 'Slide count',
    'Notes': 'Note Count',
    'HiddenSlides': 'Hidden Slide Count',
}
for element in app_xml.getchildren():
    for key, title in app_mapping.items():
        if key in element.tag:
            if 'date' in title.lower():
                text = dt.strptime(element.text, "%Y-%m-%dT%H:%M:%SZ")
            else:
                text = element.text
            print("{}: {}".format(title, text))
