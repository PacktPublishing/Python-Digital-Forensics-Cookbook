from __future__ import print_function
import argparse

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
__description__ = 'A simple argparse example'


parser = argparse.ArgumentParser(
    description=__description__,
    epilog="Developed by {} on {}".format(
        ", ".join(__authors__), __date__)
)

parser.add_argument("INPUT_FILE", help="Path to input file")
parser.add_argument("OUTPUT_FILE", help="Path to output file")

parser.add_argument("--hash", help="Hash the files", action="store_true")

parser.add_argument("--hash-algorithm",
                    help="Hash algorithm to use. ie md5, sha1, sha256",
                    choices=['md5', 'sha1', 'sha256'], default="sha256"
                    )

parser.add_argument("-v", "--version", "--script-version",
                    help="Displays script version information",
                    action="version", version=str(__date__)
                    )

parser.add_argument('-l', '--log', help="Path to log file", required=True)

args = parser.parse_args()

input_file = args.INPUT_FILE
output_file = args.OUTPUT_FILE

if args.hash:
    ha = args.hash_algorithm
    print("File hashing enabled with {} algorithm".format(ha))
if not args.log:
    print("Log file not defined. Will write to stdout")
