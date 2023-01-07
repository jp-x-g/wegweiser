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

headers = {"User-Agent": "JPxG's hoopty script (https://en.wikipedia.org/wiki/User:JPxG)"}

def fetch(cat):
  cat_name = urllib.parse.quote(cat, safe='') 
  url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{cat_name}&cmlimit=500"
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    print(f'Retrieved {url}')
    data = response.json()
    data = data["query"]["categorymembers"]
    return(data)
  else:
    print(f'Error retrieving {url}')
    return(f"Error retrieving {indexyear}"


if __name__ == "__main__":
  print("/!\\ This file is usually not run on its own!")
  print("cat_fetcher:")
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