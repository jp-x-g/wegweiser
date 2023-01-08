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

# namespaces = {
# "0":     "",
# "1":     "Talk:",
# "2":     "User:",
# "3":     "User talk:",
# "4":     "Wikipedia:",
# "5":     "Wikipedia talk:",
# "6":     "File:",
# "7":     "File talk:",
# "8":     "MediaWiki:",
# "9":     "MediaWiki talk:",
# "10":    "Template:",
# "11":    "Template talk:",
# "12":    "Help:",
# "13":    "Help talk:",
# "14":    "Category:",
# "15":    "Category talk:",
# "100":   "Portal:",
# "101":   "Portal talk:",
# "118":   "Draft:",
# "119":   "Draft talk:",
# "710":   "TimedText:",
# "711":   "TimedText talk:",
# "828":   "Module:",
# "829":   "Module talk:",
# "2300":  "Gadget:",
# "2301":  "Gadget talk:",
# "2302":  "Gadget definition:",
# "2303":  "Gadget definition talk:",
# "-1":    "Special:",
# "-2":    "Special talk:"
# }
# Not necessary.

headers = {"User-Agent": "JPxG's hoopty script (https://en.wikipedia.org/wiki/User:JPxG)"}

def fetch(cat, complete=False):
  cat_list = []
  cat_name = urllib.parse.quote(cat, safe='') 
  url = f"https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:{cat_name}&cmlimit=500&format=json"
  response = requests.get(url, headers=headers)
  if response.status_code == 200:
    print(f'Retrieved {url}')
    data = response.json()
    data = data["query"]["categorymembers"]
    if complete == True:
      return data
    else:
      for item in data:
        # page_name = namespaces[str(item["ns"])] + str(item["title"])
        # cat_list.append(page_name)
        cat_list.append(str(item["title"]))
      return(cat_list)
  else:
    print(f'Error retrieving {url}')
    return(f"Error retrieving {indexyear}")


if (__name__ == "__main__"):
  print("/!\\ This file is usually not run on its own!")
  print("cat_fetcher:")
  print("> fetch(cat): retrieves members of Category:Whatever,")
  print("  and returns it as an array of page names.")
  print("  Limited to 500.") 
  print("  Optional parameter 'complete=True' will return")
  print("  an array of three-item dicts, with keys")
  print("  'pageid', 'ns' and 'title'.")

  print("> main (not called from any other script):")  
  print("  Prints this message,")
  print("  fetches whatever cat you give as an arg,")
  print("  and exits.")
  print(fetch(str(sys.argv[1])))