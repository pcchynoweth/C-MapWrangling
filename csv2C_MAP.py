#!/usr/bin/python3

# csv2C_MAP.py
# FB - 201010107
# First row of the csv file must be header!

# example CSV file: 
# NAME,DESCRIPTION,LATITUDE,LONGITUDE
# WP001,Waypoint1,62 12 11.509 N,112 03 59.003 W
# WP002,Waypoint2,62 12 11.599 N,113 04 24.022 W
# WP003,Waypoint3,62 11 48.205 N,114 01 33.047 W
# WP004,Waypoint4,61 13 44.159 N,114 04 01.544 W

import csv
import string
import argparse
import sys
import time
import re
from os import path
from os import remove

parser = argparse.ArgumentParser(description="Convert C_MAP csv formatted file to C_MAP xml")
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),default=sys.stdin)
parser.add_argument('outfile')
parser.add_argument('-n', '--name', default='RT', help="specify name for the route")
parser.add_argument('-t', '--type', choices=['point', 'route', 'track'], default = 'track', help="specify type of xml file (waypoint, route, track)")
parser.add_argument('-d', '--description', default='RT_', help="specify description for the route")
parser.add_argument('-p', '--pointtype', default='4', help="specify the type of point that will be assigned to each waypoint")
parser.add_argument('-r', '--replace', default=False, action='store_true', help="if name is specified in the csv file replace it with those specified in the options")
args = parser.parse_args()
xmlRowType = {"route":"WAYPOINT", "track":"POINT", "point":"WAYPOINTS"}
xmlheaders = {"route":"<ROUTE>\n<NAME>"+"nnn"+"</NAME>\n<DESCRIPTION>" + args.description + "</DESCRIPTION>\n", "track":"<TRACK>\n", "point":"<WAYPOINTS>\n"}
xmlfooters = {"route":"</ROUTE>\n</C_MAP>\n", "track":"</TRACK>\n</C_MAP>\n", "point":"</WAYPOINTS>\n</C_MAP>\n"}
letter = string.ascii_uppercase
csvData = csv.reader(args.infile)
tags = next(csvData)
# replace spaces w/ underscores in tag names
for i in range(len(tags)):
    tags[i] = tags[i].replace(' ', '_')
# TRACK Files don't have a name, so make sure that we have one in case we want to create a ROUTE
if 'NAME' not in tags:
    tags.insert(0,'NAME')
    namePresent = False
else:
    namePresent = True
if 'TYPE' not in tags:
    tags.insert(tags.index('NAME')+1,'TYPE')
# TRACK files can have multiple segments with zeroed out latitude and longitude as the delimiter between the two segments.
# When we find one of these, we will start a new XML file.
# This regex will find the segment delimiter.

regex1 = re.compile(r"0?00\s00\.000\s(N|W|E|S)")

rowNum=0
fileNum = 1
endOfSegment = True

xmlData = args.outfile
baseFileName, baseFileExt = path.splitext(xmlData)
if "." in baseFileName:
    baseParts = baseFileName.split(".")
    baseFileName = baseParts[0]
    baseFileExt = "." + ".".join(baseParts[1:]) + baseFileExt

xmlData = open(baseFileName + "_" + '{0}'.format(fileNum) + baseFileExt, "w")
xmlRecord = '<C_MAP>' + "\n" + xmlheaders[args.type]
xmlRecord = xmlRecord.replace("<NAME>nnn","<NAME>"+args.name+letter[(fileNum-1)%len(letter)])
xmlData.write(xmlRecord)
rowWritten = False

for row in csvData:
    for item in row:
        endOfSegment = False
        if regex1.search(item):
            endOfSegment = True
            break
# TRACK Files don't have names or types, add them in with derived or specified versions
    if not endOfSegment and rowNum < 100:
        if not namePresent:
            row.insert(tags.index('NAME'),args.name + letter[fileNum-1] + "_" + '{0}'.format(rowNum))
        elif args.replace:
            row[tags.index('NAME')] = args.name + letter[fileNum-1] + "_" + '{0}'.format(rowNum)
        row.insert(tags.index('TYPE'),args.pointtype)
# At this point in the process, we have a fully populated row that can be written out as an xml item
        xmlData.write("<" + xmlRowType[args.type] + ">" + "\n")
        for tag, item in zip(tags, row):
            xmlData.write('    ' + '<' + tag + '>' \
                          + item + '</' + tag + '>' + "\n")
        xmlData.write("</" + xmlRowType[args.type] + ">" + "\n")
        rowNum +=1
        rowWritten = True
    else:
        xmlRecord = xmlfooters[args.type]
        xmlData.write(xmlRecord)
        xmlData.close()
        if not rowWritten:
            remove(xmlData.name)
        fileNum += 1
        rowNum = 0
        xmlData = open(baseFileName + "_" + '{0}'.format(fileNum) + baseFileExt, "w")
        xmlRecord = '<C_MAP>' + "\n" + xmlheaders[args.type]
        xmlRecord = xmlRecord.replace("<NAME>nnn","<NAME>"+args.name+letter[(fileNum-1)%len(letter)])
        xmlData.write(xmlRecord)
        rowWritten = False
xmlRecord = xmlfooters[args.type]
xmlData.write(xmlRecord)
xmlData.close()
if not rowWritten:
    remove(xmlData.name)
