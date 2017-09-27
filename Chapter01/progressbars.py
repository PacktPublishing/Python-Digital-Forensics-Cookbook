from __future__ import print_function
from time import sleep
import tqdm

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

fruits = [
    "Acai", "Apple", "Apricots", "Avocado", "Banana", "Blackberry",
    "Blueberries", "Cherries", "Coconut", "Cranberry", "Cucumber",
    "Durian", "Fig", "Grapefruit", "Grapes", "Kiwi", "Lemon", "Lime",
    "Mango", "Melon", "Orange", "Papaya", "Peach", "Pear", "Pineapple",
    "Pomegranate", "Raspberries", "Strawberries", "Watermelon"
]

contains_berry = 0
for fruit in tqdm.tqdm(fruits):
    if "berr" in fruit.lower():
        contains_berry += 1
    sleep(.1)
print("{} fruit names contain 'berry' or 'berries'".format(contains_berry))

contains_berry = 0
pbar = tqdm.tqdm(fruits, desc="Reviewing names", unit="fruits")
for fruit in pbar:
    if "berr" in fruit.lower():
        contains_berry += 1
    pbar.set_postfix(hits=contains_berry)
    sleep(.1)
print("{} fruit names contain 'berry' or 'berries'".format(contains_berry))

for i in tqdm.trange(10000000, unit_scale=True, desc="Trange: "):
    pass
