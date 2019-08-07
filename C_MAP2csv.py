#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 11:21:45 2019

@author: peter
"""
# C_MAP2csv.py

import argparse
from bs4 import BeautifulSoup
import csv
import re
import sys

tag = []
row = []
data = []
parser = argparse.ArgumentParser(description="Convert C_MAP xml formatted file to csv")
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),default=sys.stdin)
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'))
args = parser.parse_args()
csvfile = args.outfile
f = args.infile
writer = csv.writer(csvfile, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_ALL)
contents = f.read()
soup = BeautifulSoup(contents, 'xml')
strings = soup.find_all(re.compile('(WAY){0,1}POINT'))
if soup.POINT:
    root = soup.POINT
elif soup.WAYPOINT:
    root = soup.WAYPOINT
tag = [e.name for e in root.children if e.name is not None ]
writer.writerow(tag)
for i in strings:
    for j in i:
        if j.name:
            row.append(j.text)
    writer.writerow(row)
    row.clear()
