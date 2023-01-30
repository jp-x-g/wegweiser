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
# Usage: python3 combiner.py 2016

signpost = "Wikipedia Signpost"

###############################################################################
# This script is for mass-tagging of articles whose subpages match a mask.
# That is to say, if you want to tag all "Arbitration report" articles with
# "arbitrationreport", or whatever. 
###############################################################################

###############################################################################
# It can also fetch from categories, i.e. extract all pages from a certain cat
# and then add them to whatever tag you give as an argument.
# Like this:
# python3 mass_tagger.py 2005 Wikipedia_Signpost_Year_in_review yearinreview
###############################################################################

###############################################################################
# It can also just add a tag to every article that's in a certain list.
# This is done by specifying the fourth parameter.
# Like this:
# python3 mass_tagger.py 2005 nocat acejan2006 mass_tag.txt
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
else:
  print("You didn't specify a year.")
  print("Usage: python3 mass_tagger.py [year] [category] [tag]")
  exit()

if len(sys.argv) > 2:
  from_cat = str(sys.argv[2])
else:
  print("You didn't specify a cat.")
  print("Usage: python3 mass_tagger.py [year] [category] [tag]")
  exit()

if len(sys.argv) > 3:
  add_tag = str(sys.argv[3])
else:
  print("You didn't specify a tag.")
  print("Usage: python3 mass_tagger.py [year] [category] [tag]")
  exit()

print(sys.argv)

if len(sys.argv) > 4:
  hit_list_file = str(sys.argv[4])
  print(f"Fetching from {hit_list_file}.")
else:
  hit_list_file = "false"
  print("Fetching from category.")

print(f"Attempting to mass-tag for {combine_year}.")

lua_json = lua_wrangler.fetch(combine_year)
print(f"Fetched Lua and wrangled into JSON... Items: {len(lua_json)}")

print("what da")

if (hit_list_file != "false"):
  with open(hit_list_file, "r", encoding="utf-8") as f:
    cat_list = f.read()
  cat_list = cat_list.split("\n")
  print(f"Fetched tag list.                     Items: {len(cat_list)}")
else:
  cat_list = cat_fetcher.fetch(from_cat)
  print(f"Fetched category.                     Items: {len(cat_list)}")

cat = []

total_tags_added = 0

print(f"Size of lua_json: {sys.getsizeof(lua_json)}")

for item in cat_list:
  print(item)
  if "Wikipedia:Wikipedia Signpost/" in item:
    # Break it down so that it can be put in the module index.
    item = item.replace("Wikipedia:", "").replace(signpost+"/", "")
    # 2005-12-26/Arbitration report
    # 000000000011111111112222222222
    # 012345678901234567890123456789
    item_date = item[:10]
    # 2005-12-26
    item_subpage = item[11:]
    # Arbitration report

    for index in range(0, len(lua_json)):
      if (lua_json[index]["date"] == item_date) and (lua_json[index]["subpage"] == item_subpage):
        # We've found this item in the index.
        if "tags" not in lua_json[index]:
          pass
        elif add_tag not in lua_json[index]["tags"]:
          total_tags_added += 1
          lua_json[index]["tags"].append(add_tag)

print(f"Total tags added: {total_tags_added}")

with open("combined/combine-" + str(combine_year) + ".json", "w", encoding="utf-8") as g:
  g.write(json.dumps(lua_json, indent=2))

with open("combined/lua-" + str(combine_year) + ".txt", "w", encoding="utf-8") as h:
  h.write("return " + lua_wrangler.luaify(lua_json))

print("Success: combined/combine-" + str(combine_year) + ".json and combined/lua-" + str(combine_year) + ".txt")



print("{{Signpost series")
print(f" |type        = sidebar")
print(f" |tag         = {add_tag}")
print(f" |seriestitle = {add_tag}")
print(f" |limit       = 999")
print("}} <noinclude> This template updated to use the [[Module:Signpost]] auto-generated series templates by ~~~ on ~~~~~. Previous version is included below.")
