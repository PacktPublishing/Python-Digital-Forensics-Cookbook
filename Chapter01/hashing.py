from __future__ import print_function
import argparse
import hashlib
import os

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
__description__ = "Script to hash a file's name and contents"

available_algorithms = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512
}

parser = argparse.ArgumentParser(
    description=__description__,
    epilog="Developed by {} on {}".format(", ".join(__authors__), __date__)
)
parser.add_argument("FILE_NAME", help="Path of file to hash")
parser.add_argument("ALGORITHM", help="Hash algorithm to use",
                    choices=sorted(available_algorithms.keys()))
args = parser.parse_args()

input_file = args.FILE_NAME
hash_alg = args.ALGORITHM

file_name = available_algorithms[hash_alg]()
abs_path = os.path.abspath(input_file)
file_name.update(abs_path.encode())

print("The {} of the filename is: {}".format(
    hash_alg, file_name.hexdigest()))

file_content = available_algorithms[hash_alg]()
with open(input_file, 'rb') as open_file:
    buff_size = 1024
    buff = open_file.read(buff_size)

    while buff:
        file_content.update(buff)
        buff = open_file.read(buff_size)

print("The {} of the content is: {}".format(
    hash_alg, file_content.hexdigest()))
