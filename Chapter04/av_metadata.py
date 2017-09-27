from __future__ import print_function
import argparse
import json
import mutagen

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
__description__ = "Utility to extract metadata from A/V Filess"


def handle_id3(id3_file):
    # Definitions from http://id3.org/id3v2.4.0-frames
    id3_frames = {
        'TIT2': 'Title', 'TPE1': 'Artist', 'TALB': 'Album',
        'TXXX': 'Custom', 'TCON': 'Content Type', 'TDRL': 'Date released',
        'COMM': 'Comments', 'TDRC': 'Recording Date'}
    print("{:15} | {:15} | {:38} | {}".format("Frame", "Description",
                                              "Text", "Value"))
    print("-" * 85)

    for frames in id3_file.tags.values():
        frame_name = id3_frames.get(frames.FrameID, frames.FrameID)
        desc = getattr(frames, 'desc', "N/A")
        text = getattr(frames, 'text', ["N/A"])[0]
        value = getattr(frames, 'value', "N/A")
        if "date" in frame_name.lower():
            text = str(text)

        print("{:15} | {:15} | {:38} | {}".format(
            frame_name, desc, text, value))


def handle_mp4(mp4_file):
    # Definitions from
    # http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/QuickTime.html
    cp_sym = u"\u00A9"
    qt_tag = {
        cp_sym + 'nam': 'Title', cp_sym + 'art': 'Artist',
        cp_sym + 'alb': 'Album', cp_sym + 'gen': 'Genre',
        'cpil': 'Compilation', cp_sym + 'day': 'Creation Date',
        'cnID': 'Apple Store Content ID', 'atID': 'Album Title ID',
        'plID': 'Playlist ID', 'geID': 'Genre ID', 'pcst': 'Podcast',
        'purl': 'Podcast URL', 'egid': 'Episode Global ID',
        'cmID': 'Camera ID', 'sfID': 'Apple Store Country',
        'desc': 'Description', 'ldes': 'Long Description'}
    # Definitions from
    # http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/QuickTime.html#GenreID
    genre_ids = json.load(open('apple_genres.json'))

    print("{:22} | {}".format('Name', 'Value'))
    print("-" * 40)
    for name, value in mp4_file.tags.items():
        tag_name = qt_tag.get(name, name)
        if isinstance(value, list):
            value = "; ".join([str(x) for x in value])
        if name == 'geID':
            value = "{}: {}".format(
                value, genre_ids[str(value)].replace("|", " - "))
        print("{:22} | {}".format(tag_name, value))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("AV_FILE", help="File to extract metadata from")
    args = parser.parse_args()
    av_file = mutagen.File(args.AV_FILE)

    file_ext = args.AV_FILE.rsplit('.', 1)[-1]
    if file_ext.lower() == 'mp3':
        handle_id3(av_file)
    elif file_ext.lower() == 'mp4':
        handle_mp4(av_file)
