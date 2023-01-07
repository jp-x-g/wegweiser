# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys
# python -m pip install --upgrade luadata
# These ones are from the same directory.
import lua_wrangler
import article_fetcher
import cat_fetcher
# Usage: python3 combiner.py 2016

###############################################################################
# This script is for mass-tagging of articles whose subpages match a mask.
# That is to say, if you want to tag all "Arbitration report" articles with
# "arbitrationreport", or whatever. 
###############################################################################

###############################################################################
# Let's figure out some of our parameters, read args, and wrangle some Lua.
###############################################################################

combine_views = True
#combine_views = False
current_year  = int(datetime.datetime.now().year)
combine_year  = current_year

if len(sys.argv) > 1:
  combine_year = int(sys.argv[1])

if len(sys.argv) > 2:
  add_tag = str(sys.argv[2])
else:
  print("You didn't specify a tag.")
  exit()

print(f"Attempting to mass-tag for {combine_year}.")

lua_json = lua_wrangler.fetch(combine_year)
print(f"Fetched Lua and wrangled into JSON... Items: {len(lua_json)}")


f = open("mass_tag.txt", "r")
hit_list = f.read()
f.close()
hit_list = hit_list.split("\n")

print(hit_list)

exit()

for index in range(0, len(lua_json)):
  if "tags" not in lua_json[index]:
    pass
  else:
    pass

g = open("combined/combine-" + str(combine_year) + ".json", "w")
g.write(json.dumps(lua_json, indent=2))
g.close()

output = str(lua_json)
# Now for the truly hoopty nonsense.

outputtwo = luadata.serialize(lua_json, encoding="utf-8", indent="\t", indent_level=1)
outputtwo = "return " + outputtwo

#print(outputtwo)

h = open("combined/combinelua-" + str(combine_year) + ".txt", "w")
h.write(str(outputtwo))
h.close()

print("Success: combined/combine-" + str(combine_year) + ".json and combined/combinelua-" + str(combine_year) + ".txt")