# JPxG 2023 01 27
import datetime
import functools
import requests
import json
import urllib
import sys

import luadata

import lua_wrangler


alldata = []
"Attempting to gather all metadata."

for year in range(2005, int(datetime.datetime.now().year) + 1):
	data = lua_wrangler.fetch(year)
	print(f"{year}: {len(data)}")
	alldata.append(data)

print(f"All years fetched. Chars: {str(len(str(alldata))).zfill(5)}")

alltags    = {}
allauthors = {}



# For tags
for year in alldata:
	for item in year:
		#print(item)

		if "tags" in item:
			for tag in item["tags"]:
				if tag in alltags:
					alltags[tag] += 1
				else:
					alltags[tag] = 1

		if "authors" in item:
			for author in item["authors"]:
				if author in allauthors:
					allauthors[author] += 1
				else:
					allauthors[author] = 1

outputt = ""
outputa = ""

for key in alltags.keys():
	outputt += f"{str(key)}\t{str(alltags[key])}\n"

for key in allauthors.keys():
	outputa += f"{str(key)}\t{str(allauthors[key])}\n"


print(alltags)
print(allauthors)

f = open("statisticized-tags.txt", "w")
f.write(outputt)
f.close()
f = open("statisticized-auth.txt", "w")
f.write(outputa)
f.close()
print("Written to statisticized-tags.txt and statisticized-auth.txt")