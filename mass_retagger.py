# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import sys
# These ones are from the same directory.
import lua_wrangler
import article_fetcher
import cat_fetcher
import uploader
import weg_ver
import luadata
# Usage:
# python3 retagger.py badtag goodtag 
# or:
# python3 retagger.py alias

signpost = "Wikipedia Signpost"

###############################################################################
# This script is for mass-tagging of articles, to change one tag to another.
# For example, changing 
###############################################################################

s = requests.Session()

def get_aliases():
  page_name="Module:Signpost/aliases"
  #raw_url = "https://en.wikipedia.org/w/index.php?title=" + urllib.parse.quote(page_name, safe='') + "&action=raw"
  #source = s.get(raw_url).text
  source = lua_wrangler.fetch(page="Module:Signpost/aliases")
  print(source)
  return_dict = {}
  for key in source.keys():
    for value in source[key]:
      return_dict[value] = key
  print(return_dict)
  exit()
  return return_dict

current_year  = int(datetime.datetime.now().year)

# print(sys.argv)

if len(sys.argv) < 3 and ("alias" not in sys.argv):
  print(f"You didn't specify which tags to change.")
  quit()

change_dict = {}

mode = "normal"

if (len(sys.argv) == 4) and ((sys.argv[3] == "delete")):
  mode = "delete"

if "alias" in sys.argv:
  print("Mass retagging using aliases from Module:Signpost.")
  change_dict = get_aliases()
  # Big huge dict of every tag that's an alias.

else:
  if mode == "normal":
    print(f"""Mass retagging ("{str(sys.argv[1])}" to "{str(sys.argv[2])}").""")
  if mode == "delete":
    print(f"""Mass retagging ("{str(sys.argv[1])}" to be DELETED)!""")
  change_dict[sys.argv[1]] = sys.argv[2]
  # {"badtag": "goodtag"}

total_tags_added = 0

# Okay, three, two, one, let's jam.
for year in range(2005, (current_year + 1)):
#for year in range(2005, 2009):
  year_tags_added = 0
  year_data = lua_wrangler.fetch(year)
  print(f"Fetched and deserialized data for {year}. Items: {str(len(year_data)).zfill(4)} / Size: {str(sys.getsizeof(year_data)).zfill(6)}")
  for item in year_data:
    if "tags" in item:
      for tag in item["tags"]:
        if tag in change_dict:
          year_tags_added += 1
          total_tags_added += 1
          item["tags"].remove(tag)
          if mode != "delete":
            item["tags"].append(change_dict[tag])
  # year_data = lua_wrangler.luaify(year_data)
  print(f"Changed {str(year_tags_added).zfill(3)} ({str(total_tags_added).zfill(3)} total)")

  year_data = luadata.serialize(year_data, encoding="utf-8", indent="\t", indent_level=1)
  year_data = "return " + year_data

  if "alias" in sys.argv:
    summary = f"Aliasing tags using [[Module:Signpost/aliases]] / Wegweiser V{weg_ver.str()}"
  else:
    if mode == "delete":
      summary = f"""Aliasing tags (deleting "{str(sys.argv[1])}") / Wegweiser V{weg_ver.str()}"""
    if mode == "normal":
      summary = f"""Aliasing tags ("{str(sys.argv[1])}" to "{str(sys.argv[2])}") / Wegweiser V{weg_ver.str()}"""

  uploader.upload_str(year_data, f"Module:Signpost/index/{str(year)}", summary=summary)

print(f"Successfully uploaded.")