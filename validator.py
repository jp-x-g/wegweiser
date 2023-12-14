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
import uploader
import weg_ver
headers = weg_ver.headers()
# Usage: python3 validator.py 


###############################################################################
# Let's figure out some of our parameters, read args, and wrangle some Lua.
###############################################################################

output_json     = False
combine_views   = True
#combine_views   = False
current_year    = int(datetime.datetime.now().year)
combine_year    = current_year
update_metadata = True
upload_at_end = True
one_year = False

upload_destination = "Module talk:Signpost/index/doc"

if len(sys.argv) > 1:
  one_year = True
  combine_year = int(sys.argv[1])

years = []
print(one_year)

##### If a year is specified by argument, do only that year.
##### Otherwise, do them all up to the current year.
if one_year == False:
  for year in range(2005, combine_year + 1):
    years.append(year)
else:
  years.append(combine_year)


print(f"Attempting to validate data for {str(years)}")

validate_array = []
failed_array = []
fields = ["year", "items", "date", "subpage", "title", "authors", "tags", "views"]

for year in years:
  validate_dict = {}
  failed = {}
  for each in fields:
    validate_dict[each] = 0
    failed[each] = []

  # Catch edge cases.
  validate_dict["year"] = int(year)
  failed["year"] = int(year)
  failed["items"] = 0

  # Initialize empty dicts, using fields from the "fields" array.

  ##### Actually hit the API to get the JSON of the Lua table.
  lua_json = lua_wrangler.fetch(year)
  print(f"Fetched Lua and wrangled into JSON... Items: {len(lua_json)}")
  validate_dict["items"] = len(lua_json)

  ##### Iterate over each item in the JSON and see if it's got all the fields.
  for item in lua_json:
    #print(item)
    for field in validate_dict:
      if (field == "views") and (year < 2015):
        validate_dict["views"] = -1
      else:
        if field == "year" or field == "items":
          pass
        else:
          #print(validate_dict[field])
          if field in item:
            validate_dict[field] += 1
          else:
            failed["items"] += 1
            failed[field].append(str(item["date"]) + "/" + str(item["subpage"]))

  ##### Now we have validation data for that year, let's print it.
  #print(validate_dict)
  #print(failed)
  validate_array.append(validate_dict)
  failed_array.append(failed)

##### Done processing all years, let's output the JSON and make a table.
print(json.dumps(validate_array, indent=2))

table_string = '{| class="wikitable sortable"'
for field in validate_dict:
  # Make table headers.
  table_string += f"\n! {str(field)}"
for item in validate_array:
  table_string += f"\n|-"
  for field_name in fields:
    print(field_name)
    table_string += f"\n| {str(item[field_name])}"

table_string += "\n|}"

print(table_string)

broken_string = "== Items missing metadata =="
print(json.dumps(failed_array, indent=2))

try:
  for year in failed_array:
    broken_string += f"\n=== {year['year']} ({str(year['items'])}) ==="
    broken_string += f"\n* [[Module:Signpost/index/{year['year']}]] / [https://en.wikipedia.org/w/index.php?title=Module:Signpost/index/{year['year']}&action=edit edit]"
    for fail in year.keys():
      if (fail != "year") and (fail != "items"):
        failcount = 0
        broken_string_add = f"\n==== {fail} ===="
        for page in year[fail]:
          failcount += 1
          broken_string_add += f"\n# [[Wikipedia:Wikipedia Signpost/{page}]]"
        if failcount > 0:
          broken_string += broken_string_add
except Exception as err:
 print(err)
 print(broken_string)

print(broken_string)


output_string = "== Table of indices =="
output_string += "\n"
output_string += "__TOC__"
output_string += "\n<onlyinclude>"
output_string += table_string
output_string += "\n</onlyinclude>"
output_string += broken_string

file_name = "data/validate.txt"

f = open(file_name, "w")
f.write(output_string)
f.close()

uploader.upload(file_name, "Wikipedia:Wikipedia_Signpost/Technical/Index_validation", summary=f"validator.py, Wegweiser V{weg_ver.str()}")