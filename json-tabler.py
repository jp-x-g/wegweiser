# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys

print(f"Opening {sys.argv[1]}...")

f = open(sys.argv[1], "r")
data = f.read()
f.close()

print(f"File opened. Processing {len(data)} chars.")

data = json.loads(data)

output = ""
for a in data:
    for item in data[a]:
        # print(item)
        output+= str(item["date"]) + "\t" + str(item["subpage"]) + "\t" + str(item["views"]) + "\n"
        print(str(item["date"]) + "\t" + str(item["subpage"]) + "\t" + str(item["views"]))

outpath = "output.txt"

if len(sys.argv) > 2:
    outpath = sys.argv[1]

g = open(outpath, "w")
g.write(output)
g.close()

print(f"Written to {sys.argv[1]}")
print("All done, boss!")