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
import weg_ver
headers = weg_ver.headers()
# Usage: python3 combiner.py 2016

def updateArray(baseArray, updateArray):
    """
    baseArray is the one you want to update, using entries from updateArray.
    This will add them if they're missing, but won't alter entries already
    in baseArray: if they have more detailed information, they'll be kept.
    """
    # My previous version was O(n^2), but this one is O(n).
    # Thanks, ChatGPT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    baseDict = {}
    for item in baseArray:
        key = (item['date'], item['subpage'])
        baseDict[key] = item

    updateDict = {}
    for item in updateArray:
        key = (item['date'], item['subpage'])
        updateDict[key] = item

    #print(baseDict)
    
    for i in range(len(updateArray)):
        key = (updateArray[i]['date'], updateArray[i]['subpage'])
        if key not in baseDict:
            #print(key)
            baseArray.append(updateDict[key])
    return baseArray

def updateArrayItems(baseArray, updateArray):
    """
    This will update keys in array items, rather than the items themselves.
    For example, if you want to fill in missing "title" fields for articles,
    or "author" fields or whatever -- but NOT if the destination array already
    has those fields. If they've been filled in manually, we leave them alone.
    """
    for i in range(len(baseArray)):
      #print(i)
      #print(baseArray[i])
      # For every entry in the base array...
      for j in range(len(updateArray)):
        #print(j)
        #print(updateArray[j])
        # Go over every entry in the updating array.
        if (baseArray[i]["date"] == updateArray[j]["date"]) and (baseArray[i]["subpage"] == updateArray[j]["subpage"]):
          #print(baseArray[i])
          #print(updateArray[j])
          #print("Match!")
          # And if it matches the entry in the base array...
          for key in updateArray[j]:
            # Go through every key in the updating array....
            if key not in (baseArray[i]) or (baseArray[i][key] == "unparsed") or (baseArray[i][key] == ["unparsed"]) or (baseArray[i][key] == "none") or (baseArray[i][key] == ["none"]) or (baseArray[i][key] == "") or (baseArray[i][key] == [""]):
              # and add the key/value to baseArray... if it doesn't already exist.
              if updateArray[j][key] != "unparsed":
                #Unless it's "unparsed".
                baseArray[i][key] = updateArray[j][key]
            if key in baseArray[i]:
              # But if there's already something for that key, don't do anything.
              pass
          break
          # No need to keep going over the update array if you already found the match.
    return baseArray

###############################################################################
# Let's figure out some of our parameters, read args, and wrangle some Lua.
###############################################################################

output_json     = False
combine_views   = True
#combine_views   = False
current_year    = int(datetime.datetime.now().year)
combine_year    = current_year
update_metadata = True

if len(sys.argv) > 1:
  combine_year = int(sys.argv[1])

print(f"Attempting to combine for {combine_year}.")

lua_json = lua_wrangler.fetch(combine_year)
print(f"Fetched Lua and wrangled into JSON... Items: {len(lua_json)}")

#print(lua_json)
#print(json.dumps(lua_json, indent=2))
#print(lua_json[0])



###############################################################################
# Below is the part that adds articles to indices that lack them.
###############################################################################
# This has to be done before anything else, because sometimes the Lua tables
# won't have every article in them (if forgotten, or published very recently).
# If the articles aren't in the table, we can't update them with other stuff.
#
# This doesn't upsert: if an article has an entry in lua_json, it's left alone.

all_articles = article_fetcher.fetch(combine_year, combine_year, 13, format="dict")

all_articles = all_articles[str(combine_year)]

print(f"Fetched PrefixIndex article list..... Items: {len(all_articles)}")

lua_json = updateArray(lua_json, all_articles)

###############################################################################
# Below is the part that integrates metadata (authors, titles, etc).
###############################################################################

if update_metadata == True:

  file_path = "metadata/" + str(combine_year) + "-metadata.txt"
  f = open(file_path, "r")
  meta_data = f.read()
  f.close()
  meta_data = json.loads(meta_data)
  meta_data = meta_data[str(combine_year)]
  
  lua_json = updateArrayItems(lua_json, meta_data)


###############################################################################
# Below is the part that integrates viewcounts.
###############################################################################
# This way of doing it force-updates the Lua table with the new data,
# overwriting already-present values, so should be used only where values in
# out JSON is canonically "more correct" i.e. the view counts which may change
# over time. It shouldn't be used for stuff where the Lua may be more correct.

if combine_year < 2015:
  print("Skipping pageview statistics (year is before May 2015)")
  # Pageview statistics only exist for May 2015 and later.
  combine_views = False

if combine_views == True:

  file_path = "views/" + str(combine_year) + "-views.txt"
  f = open(file_path, "r")
  views_data = f.read()
  f.close()
  views_data = json.loads(views_data)
  # Load as JSON.
  views_data = views_data[str(combine_year)]
  # Get views_data["2017"] or whatever.

  for index in range(0, len(lua_json)):
    for my_item in views_data:
      if (my_item["date"] == lua_json[index]["date"]) and (my_item["subpage"] == lua_json[index]["subpage"]):
        if "views" not in my_item:
          print(f"ERROR: No views for {str(my_item)}")
          my_item["views"] = {
          'd007': -1,
          'd015': -1,
          'd030': -1,
          'd060': -1,
          'd090': -1,
          'd120': -1,
          'd180': -1
          }
        lua_json[index]["views"] = my_item["views"]
        #print(lua_json[index])
        break



  """
  Old version, with keys like "views007", "views015", etc.
  for day_range in [7, 30, 60, 90, 120, 180]:
    views_day = "views" + str(day_range).zfill(3)
    fdata = fdata[str(combine_year)]
    #print(fdata)
    for index in range(0, len(lua_json)):
      for my_item in fdata:
        if (my_item["date"] == lua_json[index]["date"]) and (my_item["subpage"] == lua_json[index]["subpage"]):
          lua_json[index][views_day] = my_item[views_day]
          #print(lua_json[index])
          break
    print("Views integrated.")
  """


#TODO: whatever
#output = {"2022": indytwo}
#output = json.dumps(output, indent=2)

# print(lua_json)

if output_json == True:
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

h = open("combined/lua-" + str(combine_year) + ".txt", "w")
h.write(str(outputtwo))
h.close()
if output_json == True:
  print("Success: combined/combine-" + str(combine_year) + ".json and combined/lua-" + str(combine_year) + ".txt")
else:
  print("Success: combined/lua-" + str(combine_year) + ".txt")