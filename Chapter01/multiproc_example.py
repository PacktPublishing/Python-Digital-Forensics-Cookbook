from __future__ import print_function
import logging
import multiprocessing as mp
from random import randint
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


def sleepy(seconds):
    proc_name = mp.current_process().name
    logger.info("{} is sleeping for {} seconds.".format(
        proc_name, seconds))
    time.sleep(seconds)


logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
msg_fmt = logging.Formatter("%(asctime)-15s %(funcName)-7s "
                            "%(levelname)-8s %(message)s")
strhndl = logging.StreamHandler(sys.stdout)
strhndl.setFormatter(fmt=msg_fmt)
logger.addHandler(strhndl)

num_workers = 5
workers = []
for w in range(num_workers):
    p = mp.Process(target=sleepy, args=(randint(1, 20),))
    p.start()
    workers.append(p)

for worker in workers:
    worker.join()
    logger.info("Joined process {}".format(worker.name))
