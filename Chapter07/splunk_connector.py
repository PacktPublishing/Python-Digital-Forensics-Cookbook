from __future__ import print_function
from argparse import ArgumentParser, ArgumentError
from argparse import ArgumentDefaultsHelpFormatter
import splunklib.client as client
import splunklib.results as results
import os
import sys
import csv

if sys.version_info.major != 2:
    print("Invalid python version. Must use Python 2 due to splunk api "
          "library")

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
__description__ = "Utility to ingest, query, and export data with Splunk"


class Spelunking(object):
    def __init__(self, service, action, index_name, cols):
        self.service = service
        self.action = action
        self.index = index_name
        self.file = None
        self.query = None
        self.sid = None
        self.job = None
        self.cols = cols

    def run(self):
        index_obj = self.get_or_create_index()
        if self.action == 'index':
            self.index_data(index_obj)
        elif self.action == 'query':
            self.query_index()
        elif self.action == 'export':
            self.export_report()
        return

    def get_or_create_index(self):
        # Create a new index
        if self.index not in self.service.indexes:
            return service.indexes.create(self.index)
        else:
            return self.service.indexes[self.index]

    def index_data(self, splunk_index):
        splunk_index.upload(self.file)

    def query_index(self):
        self.query = self.query + "| fields + " + ", ".join(self.cols)
        self.job = self.service.jobs.create(self.query, rf=self.cols)
        self.sid = self.job.sid
        print("Query job {} created. will expire in {} seconds".format(
            self.sid, self.job['ttl']))

    def export_report(self):
        job_obj = None
        for j in self.service.jobs:
            if j.sid == self.sid:
                job_obj = j

        if job_obj is None:
            print("Job SID {} not found. Did it expire?".format(self.sid))
            sys.exit()

        if not job_obj.is_ready():
            print("Job SID {} is still processing. "
                  "Please wait to re-run".format(self.sir))

        export_data = []
        job_results = job_obj.results(rf=self.cols)
        for result in results.ResultsReader(job_results):
            export_data.append(result)

        self.write_csv(self.file, self.cols, export_data)

    @staticmethod
    def write_csv(outfile, fieldnames, data):
        with open(outfile, 'wb') as open_outfile:
            csvfile = csv.DictWriter(open_outfile, fieldnames,
                                     extrasaction="ignore")
            csvfile.writeheader()
            csvfile.writerows(data)


if __name__ == '__main__':
    parser = ArgumentParser(
        description=__description__,
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument('action', help="Action to run",
                        choices=['index', 'query', 'export'])
    parser.add_argument('--index-name', help="Name of splunk index",
                        required=True)
    parser.add_argument('--config',
                        help="Place where login details are stored."
                        " Should have the username on the first line and"
                        " the password on the second."
                        " Please Protect this file!",
                        default=os.path.expanduser("~/.splunk_py.ini"))
    parser.add_argument('--file', help="Path to file")
    parser.add_argument('--query', help="Splunk query to run or sid of "
                        "existing query to export")
    parser.add_argument(
        '--cols',
        help="Speficy columns to export. comma seperated list",
        default='_time,date,time,sc_status,c_ip,s_ip,cs_User_Agent')
    parser.add_argument('--host', help="hostname of server",
                        default="localhost")
    parser.add_argument('--port', help="help", default="8089")
    args = parser.parse_args()

    with open(args.config, 'r') as open_conf:
        username, password = [x.strip() for x in open_conf.readlines()]
    conn_dict = {'host': args.host, 'port': int(args.port),
                 'username': username, 'password': password}
    del(username)
    del(password)
    service = client.connect(**conn_dict)
    del(conn_dict)

    if len(service.apps) == 0:
        print("Login likely unsuccessful, cannot find any applications")
        sys.exit()

    cols = args.cols.split(",")
    spelunking = Spelunking(service, args.action, args.index_name, cols)

    if spelunking.action == 'index':
        if 'file' not in vars(args):
            ArgumentError('--file parameter required')
            sys.exit()
        else:
            spelunking.file = os.path.abspath(args.file)

    elif spelunking.action == 'export':
        if 'file' not in vars(args):
            ArgumentError('--file parameter required')
            sys.exit()
        if 'query' not in vars(args):
            ArgumentError('--query parameter required')
            sys.exit()
        spelunking.file = os.path.abspath(args.file)
        spelunking.sid = args.query

    elif spelunking.action == 'query':
        if 'query' not in vars(args):
            ArgumentError('--query parameter required')
            sys.exit()
        else:
            spelunking.query = "search index={} {}".format(args.index_name,
                                                           args.query)

    else:
        ArgumentError('Unknown action required')
        sys.exit()

    spelunking.run()
