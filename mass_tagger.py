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

signpost = "Wikipedia Signpost"

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

print(f"Attempting to mass-tag for {combine_year}.")

lua_json = lua_wrangler.fetch(combine_year)
print(f"Fetched Lua and wrangled into JSON... Items: {len(lua_json)}")


#f = open("mass_tag.txt", "r")
#hit_list = f.read()
#f.close()
#hit_list = hit_list.split("\n")

#print(hit_list)

cat_list = cat_fetcher.fetch(from_cat)
print(f"Fetched category.                     Items: {len(cat_list)}")

cat = []

total_tags_added = 0

print(f"Size of lua_json: {sys.getsizeof(lua_json)}")

for item in cat_list:
  if "Wikipedia:Wikipedia Signpost/" in item:
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

g = open("combined/combine-" + str(combine_year) + ".json", "w")
g.write(json.dumps(lua_json, indent=2))
g.close()

output = str(lua_json)
# Now for the truly hoopty nonsense.

outputtwo = luadata.serialize(lua_json, encoding="utf-8", indent="\t", indent_level=1)
outputtwo = "return " + outputtwo

# Make the sub-lists for tags be on one line instead of indented quadrice on multiple lines.
outputtwo = outputtwo.replace('\n\t\t\t\t"', ' "')
# Replace "tab tab {" with "tab {"
outputtwo = outputtwo.replace("\n\t\t{", "\n\t{")
# Replace "tab tab tab }" for sub-lists with normal closing brace.
outputtwo = outputtwo.replace("\n\t\t\t}", " }")
# De-indent individual items in 
outputtwo = outputtwo.replace("\n\t\t\t", "\n\t\t")
#print(outputtwo)

h = open("combined/combinelua-" + str(combine_year) + ".txt", "w")
h.write(str(outputtwo))
h.close()

print("Success: combined/combine-" + str(combine_year) + ".json and combined/combinelua-" + str(combine_year) + ".txt")