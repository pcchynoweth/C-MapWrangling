#!/usr/bin/python
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
import argparse
import sys
import time
import re
parser = argparse.ArgumentParser(description="Convert C_MAP csv formatted file to C_MAP xml")
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),default=sys.stdin)
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),default=sys.stdout)
parser.add_argument('-n', '--name', default='RT', help="specify name for the route")

parser.add_argument('-t', '--type', choices=['point', 'route', 'track'], default = 'track', help="specify type of xml file (waypoint, route, track)")
args = parser.parse_args()
csvData = csv.reader(args.infile)
xmlData = args.outfile
# there must be only one top-level tag
xmlRecord = '<C_MAP>' + "\n"
if args.type == "route":
  xmlRecord += '<ROUTE>' + "\n"
  xmlRecord += '<NAME>' + args.name + '</NAME>' + '\n'
  xmlRowType = 'WAYPOINT'
elif args.type == 'track':
  xmlRecord += '<TRACK>' + "\n"
  xmlRowType = 'POINT' 
elif args.type == 'point':
  xmlRecord += '<WAYPOINTS>' + "\n"
  xmlRowType = 'WAYPOINT'
xmlData.write(xmlRecord)
tags = csvData.next()
# replace spaces w/ underscores in tag names
for i in range(len(tags)):
  tags[i] = tags[i].replace(' ', '_')
# TRACK Files don't have a name, so make sure that we have one in case we want to create a ROUTE
if 'NAME' not in tags:
  tags.insert(0,'NAME')
# files should also have a description, so insert one after the name, if required
if ('DESCRIPTION' not in tags) and ('DESC' not in tags):
	tags.insert(tags.index('NAME')+1,'DESCRIPTION')
rowNum=1
# TRACK files can have extra rows with zeroed out latitude and longitude, this regex will find them
regex = re.compile(r"0?00\s00\.000\s(N|W|E|S)")

for row in csvData:
# This is the equivalent of "for 'regex' in list: Search for the regex and set a switch if found
  for item in row:
	extraRow = False
	if regex.search(item):
	  extraRow = True
	  break
# TRACK Files don't have names or descriptions, add them in with derived versions
  if not extraRow:
	while len(row) < len(tags):
		row.insert(0,args.name + '{0}'.format(rowNum))
# At this point in the process, we have a 
	xmlData.write('<' + xmlRowType + '>' + "\n")
	for tag, item in zip(tags, row):
		xmlData.write('    ' + '<' + tag + '>' \
                          + item + '</' + tag + '>' + "\n")
	xmlData.write('</' + xmlRowType + '>' + "\n")
	rowNum +=1
if args.type == "route":
  xmlRecord = '</ROUTE>'
elif args.type == 'track':
  xmlRecord = '</TRACK>'
elif args.type == 'point' :
  xmlRecord = '</WAYPOINTS>'
xmlData.write(xmlRecord + '\n' + '</C_MAP>' + '\n')
xmlData.close()

