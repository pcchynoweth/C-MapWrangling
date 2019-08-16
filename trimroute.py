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
import argparse
import sys
from pygeodesy import dms
from geopy.distance import vincenty
 
parser = argparse.ArgumentParser(description="Trim a CSV file with route information to eliminate extraneous points")
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),default=sys.stdin)
parser.add_argument('-r', '--removed_file', required=False, help="optionally specify a file name for the removed points")
parser.add_argument('-d', '--diff_file', required=False,help="optionally specify a file name for the file of differences")
parser.add_argument('-t', '--threshhold', default='.25', help="specify the threshhold in metres for close points")
parser.add_argument('-o', '--outfile',type=argparse.FileType('w'), help="optionally specify an output file name", default=sys.stdout) 
args = parser.parse_args()
csvData = csv.reader(args.infile)
tags = next(csvData)
tags = [element.upper() for element in tags]
if "LONG" in tags:
	tags[tags.index('LONG')] = "LONGITUDE"
if "LAT" in tags:
	tags[tags.index('LAT')] = "LATITUDE"
if not set(['LATITUDE','LONGITUDE']).issubset( tags ):
    raise Exception("LATITUDE and LONGITUDE are required but missing")
row1 = next(csvData)
row2 = next(csvData)
deleted_points=[tags]
new_route=[tags,row1]
differences=[]
for row in csvData:
    row3 = row
    point1 = (dms.parseDMS(row1[tags.index('LATITUDE')]),dms.parseDMS(row1[tags.index('LONGITUDE')]))
    point2 = (dms.parseDMS(row2[tags.index('LATITUDE')]),dms.parseDMS(row2[tags.index('LONGITUDE')]))
    point3 = (dms.parseDMS(row3[tags.index('LATITUDE')]),dms.parseDMS(row3[tags.index('LONGITUDE')]))
    distance1=vincenty(point1,point2).m
    distance2=vincenty(point2,point3).m
    distance3=vincenty(point1,point3).m
    distance4=distance1+distance2
    if args.diff_file:
       if 'NAME' in tags:
           rowname=row2[tags.index('NAME')]
       else:
           rowname="Name not present"
       differences.append ((rowname,point1,point2,point3,distance1,distance2,distance3,distance4,args.threshhold))
    if (distance4-distance3) < float(args.threshhold):
        deleted_points.append(row2)
    else:
        new_route.append(row2)
        row1=row2
    row2=row3
new_route.append(row3)
for i in range(0,len(new_route)):
    args.outfile.write(",".join(new_route[i])+"\n")
if args.removed_file:
    with open(args.removed_file, "w") as df:
        for i in range(0,len(deleted_points)):
            df.write(",".join(deleted_points[i])+"\n")
if args.diff_file:
    with open(args.diff_file, "w") as of:
        for i in range(0,len(differences)):
            of.write(str(differences[i])+"\n")
