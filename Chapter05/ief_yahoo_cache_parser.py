from __future__ import print_function
import argparse
import csv
import json
import os
import sqlite3
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
__description__ = "Utility to extract Yahoo! webmail contacts from IEF"


def main(database, out_csv):
    print("[+] Connecting to SQLite database")
    conn = sqlite3.connect(database)
    c = conn.cursor()

    print("[+] Querying IEF database for Yahoo Contact Fragments from "
          "the Chrome Cache Records Table")
    try:
        c.execute(
            "select * from 'Chrome Cache Records' where URL like "
            "'https://data.mail.yahoo.com"
            "/classicab/v2/contacts/?format=json%'")
    except sqlite3.OperationalError:
        print("Received an error querying the database -- database may be"
              "corrupt or not have a Chrome Cache Records table")
        sys.exit(2)

    contact_cache = c.fetchall()
    contact_data = process_contacts(contact_cache)
    write_csv(contact_data, out_csv)


def process_contacts(contact_cache):
    print("[+] Processing {} cache files matching Yahoo contact cache "
          " data".format(len(contact_cache)))
    results = []
    for contact in contact_cache:
        url = contact[0]
        first_visit = contact[1]
        last_visit = contact[2]
        last_sync = contact[3]
        loc = contact[8]
        contact_json = json.loads(contact[7].decode())
        total_contacts = contact_json["total"]
        total_count = contact_json["count"]

        if "contacts" not in contact_json:
            continue

        for c in contact_json["contacts"]:
            name, anni, bday, emails, phones, links = (
                "", "", "", "", "", "")
            if "name" in c:
                name = c["name"]["givenName"] + " " + \
                    c["name"]["middleName"] + " " + c["name"]["familyName"]
            if "anniversary" in c:
                anni = c["anniversary"]["month"] + \
                    "/" + c["anniversary"]["day"] + "/" + \
                    c["anniversary"]["year"]
            if "birthday" in c:
                bday = c["birthday"]["month"] + "/" + \
                    c["birthday"]["day"] + "/" + c["birthday"]["year"]
            if "emails" in c:
                emails = ', '.join([x["ep"] for x in c["emails"]])
            if "phones" in c:
                phones = ', '.join([x["ep"] for x in c["phones"]])
            if "links" in c:
                links = ', '.join([x["ep"] for x in c["links"]])

            company = c.get("company", "")
            title = c.get("jobTitle", "")
            notes = c.get("notes", "")

            results.append([
                url, first_visit, last_visit, last_sync, loc, name, bday,
                anni, emails, phones, links, company, title, notes,
                total_contacts, total_count])
    return results


def write_csv(data, output):
    print("[+] Writing {} contacts to {}".format(len(data), output))
    with open(output, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([
            "URL", "First Visit (UTC)", "Last Visit (UTC)",
            "Last Sync (UTC)", "Location", "Contact Name", "Bday",
            "Anniversary", "Emails", "Phones", "Links", "Company", "Title",
            "Notes", "Total Contacts", "Count of Contacts in Cache"])
        csv_writer.writerows(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("IEF_DATABASE", help="Input IEF database")
    parser.add_argument("OUTPUT_CSV", help="Output CSV")
    args = parser.parse_args()

    directory = os.path.dirname(args.OUTPUT_CSV)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if os.path.exists(args.IEF_DATABASE) and \
            os.path.isfile(args.IEF_DATABASE):
        main(args.IEF_DATABASE, args.OUTPUT_CSV)
    else:
        print(
            "[-] Supplied input file {} does not exist or is not a "
            "file".format(args.IEF_DATABASE))
        sys.exit(1)
