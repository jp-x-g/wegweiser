# JPxG 2023 01 27
import datetime
import functools
import requests
import json
import urllib
import sys

import luadata

import lua_wrangler
import tsv_to_wikitable
import uploader

import weg_ver

tags_path = "data/statisticized-tags.txt"
auth_path = "data/statisticized-auth.txt"

def biglist():
	return [
	"Authors to search for",
	"Just put em in the list"
	]


testlist = ["asdf", "asdf2"]

big_list = biglist()
# print(big_list)

alldata = []
"Attempting to gather all metadata."

for year in range(2005, int(datetime.datetime.now().year) + 1):
	data = lua_wrangler.fetch(year)
	print(f"{year}: {len(data)}")
	alldata.append(data)

print(f"All years fetched. Chars: {str(len(str(alldata))).zfill(5)}")

alltags    = {}
allauthors = {}
badshit    = ""

# For tags
for year in alldata:
	for item in year:
		#print(item)

		if "tags" in item:
			for tag in item["tags"]:
				if tag in alltags:
					alltags[tag][0] += 1
					# Increment the number of articles with that tag...
					alltags[tag][1] = item["date"]
					# and the date of the most recent.
				else:
					alltags[tag] = [1, item["date"]]

		if "authors" in item:
			for author in item["authors"]:
				if author.strip() in big_list:
					print(item)
					badshit += "\n"
					# badshit += f"# [[Wikipedia:Wikipedia Signpost/{item['date']}/{item['subpage']}]]"
					badshit += f"Wikipedia:Wikipedia Signpost/{item['date']}/{item['subpage']}"
				if author in allauthors:
					allauthors[author][0] += 1
					# Increment the number of articles written by the author...
					allauthors[author][1] = item["date"]
					# and the date of their most recent article.
				else:
					allauthors[author] = [1, item["date"]]



outputt = ""
outputa = ""

for key in sorted(alltags.keys()):
	outputt += f"{str(key)}\t{str(alltags[key][0])}\t{str(alltags[key][1])}\n"

for key in sorted(allauthors.keys()):
	outputa += f"{str(key)}\t{str(allauthors[key][0])}\t{str(allauthors[key][1])}\n"


print(alltags)
print(allauthors)

#f = open("test-searchlist.txt", "w")
#f.write(str(badshit))
#f.close()


outputa = tsv_to_wikitable.process(outputa, headers=[f"Author ({str(len(allauthors))} total)", "#", "Most recent"])
outputt = tsv_to_wikitable.process(outputt, headers=[f"Tag ({str(len(alltags))} total)", "#", "Most recent"])

# Now to upload them.
uploader.upload_str(outputt, "Wikipedia:Wikipedia Signpost/Statistics/Tags/Table", summary=f"Update tag information / Wegweiser V{weg_ver.str()}")
uploader.upload_str(outputa, "Wikipedia:Wikipedia Signpost/Statistics/Authors/Table", summary=f"Update author information / Wegweiser V{weg_ver.str()}")

# Write them to disk as well.
f = open(tags_path, "w")
f.write(outputt)
f.close()
f = open(auth_path, "w")
f.write(outputa)
f.close()
print(f"Written to {tags_path} and {auth_path}")

exit()