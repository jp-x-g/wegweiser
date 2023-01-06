# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys
# python -m pip install --upgrade luadata
import lua_wrangler
# This one is from the same directory.

# TODO: Come up with some way to gracefully parse in the module indices. This is horrific.

current_year = int(datetime.datetime.now().year)
combine_year = current_year

if len(sys.argv) > 1:
  combine_year = sys.argv[1]

lua_json = lua_wrangler.fetch(combine_year)

#print(lua_json)
#print(json.dumps(lua_json, indent=2))

# This force-updates the Lua table with the new data, overwriting it if it's already present.
# Therefore, it should only be done for things where the JSON is canonically "more correct"
# i.e. the view counts (which may change over time). It shouldn't be used for other stuff.
for day_range in [7, 30, 60, 90, 120, 180]:
  views_day = "views" + str(day_range).zfill(3)
  file_path = "views/" + str(combine_year) + "-" + str(day_range) + ".txt"
  f = open(file_path, "r")
  fdata = f.read()
  f.close()
  fdata = json.loads(fdata)
  fdata = fdata[str(combine_year)]
  #print(fdata)
  for index in range(0, len(lua_json)):
    for my_item in fdata:
      if (my_item["date"] == lua_json[index]["date"]) and (my_item["subpage"] == lua_json[index]["subpage"]):
        lua_json[index][views_day] = my_item[views_day]
        print(lua_json[index])
        break
  print("huzzah")


#TODO: whatever
#output = {"2022": indytwo}
#output = json.dumps(output, indent=2)

# print(lua_json)

g = open("combined/combined-" + combine_year + ".json", "w")
g.write(json.dumps(lua_json, indent=2))
g.close()

output = str(lua_json)
# Now for the truly hoopty nonsense.

outputtwo = luadata.serialize(lua_json, encoding="utf-8", indent="\t", indent_level=1)

print(outputtwo)

h = open("combined/lua-" + combine_year + ".txt", "w")
h.write(str(outputtwo))
h.close()