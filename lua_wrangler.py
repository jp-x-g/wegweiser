# JPxG 2023 01 04
import datetime
import functools
import requests
import json
import urllib
import sys

import luadata

import lua_serializer

import weg_ver

def fetch(indexyear=2005, page=""):
  headers = weg_ver.headers()

  # If you pass "page" into this function, it will override the year parsing.
  if page == "":
    page_name = f"Module:Signpost/index/{str(indexyear)}"
  else:
    page_name = page

  page_name = urllib.parse.quote(page_name, safe='')
  url = f"https://en.wikipedia.org/w/api.php?action=parse&page={page_name}&prop=wikitext&format=json&formatversion=2"
  print(url)
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    print(f'Retrieved {url}')
    data = response.json()
    data = data["parse"]["wikitext"]
    if data == "":
        return("")
    else:
        data_parsed = luadata.unserialize(data, encoding="utf-8", multival=False)
        #luadata.unserialize(data, encoding="utf-8", multival=False, verbose=True)
        return(data_parsed)
  else:
    print(f'Error retrieving {url}')
    return(f"Error retrieving {indexyear}")

table_key_priorities = {
    "date":    0,
    "subpage": 1,
    "title":   2,
    "subhead": 3,
    "authors": 4,
    "piccy":   5,
    "tags":    6,
    "views":   7
}


def compare_table_keys(a, b):
    a_priority = table_key_priorities.get(a)
    b_priority = table_key_priorities.get(b)
    if a_priority is not None and b_priority is not None:
        return -1 if a_priority < b_priority else 1
    elif a_priority is not None:
        return -1
    elif b_priority is not None:
        return 1
    else:
        return -1 if a < b else 1

def luaify(obj):
    headers = weg_ver.headers()
    return lua_serializer.serialize(
        obj,
        indent="\t",
        min_single_line_indent_level=2,
        table_sort_key=functools.cmp_to_key(compare_table_keys),
    )

if __name__ == "__main__":
  print("/!\\ This file is usually not run on its own!")
  print("lua_wrangler.py has several functions:")
  print("> fetch(year): retrieves wikitext of Module:Signpost/index/year,")
  print("  converts Lua table to a Python object, and returns it.")
  print("> luaify(obj): serializes a Python object to a Lua table.")
  print("> main (not called from any other script):")
  print("  print this message, retrieve and print index for CURRENTYEAR,")
  print("  and (optionally) save it to an output file, viz.")
  print("  \"python3 lua_wrangler.py output.txt\" or whatever.")

  current_year = int(datetime.datetime.now().year)
  output = fetch(current_year)
  print(output)
  print(json.dumps(output, indent=2))
  if len(sys.argv) > 1:
    f = open(str(sys.argv[1]), "w")
    f.write(json.dumps(output, indent=2))
    f.close()

  print(luaify(output))
