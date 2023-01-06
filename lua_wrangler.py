# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys

headers = {"User-Agent": "JPxG's hoopty script (https://en.wikipedia.org/wiki/User:JPxG)"}

def fetch(indexyear):
  page_name = f"Module:Signpost/index/{str(indexyear)}"
  page_name = urllib.parse.quote(page_name, safe='')
  url = f"https://en.wikipedia.org/w/api.php?action=parse&page={page_name}&prop=wikitext&format=json&formatversion=2"
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    print(f'Retrieved {url}')
    data = response.json()
    data = data["parse"]["wikitext"]
    data_parsed = luadata.unserialize(data, encoding="utf-8", multival=False)
    #luadata.unserialize(data, encoding="utf-8", multival=False, verbose=True)
    return(data_parsed)
  else:
    print(f'Error retrieving {url}')
    return(f"Error retrieving {indexyear}")

def luaify(some_json, indent=1):
    return luadata.serialize(some_json, encoding="utf-8", indent="\t", indent_level=indent)

if __name__ == "__main__":
  print("/!\\ This file is usually not run on its own!")
  print("lua_wrangler.py has several functions:")
  print("> fetch(year): retrieves wikitext of Module:Signpost/index/year,")
  print("  converts Lua table to JSON, and returns it.")
  print("> luaify(json): returns JSON serialized to a Lua table.")
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