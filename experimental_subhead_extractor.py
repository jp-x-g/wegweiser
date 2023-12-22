# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys
import mwparserfromhell
# python -m pip install --upgrade luadata
import article_fetcher
from bs4 import BeautifulSoup
import weg_ver
import uploader
import os
import platform

headers = weg_ver.headers()
# This is a secret tool that will come in handy later.
signpost = "Wikipedia Signpost"
current_year = int(datetime.datetime.now().year)
current_month = datetime.datetime.now().month
current_day = datetime.datetime.now().day
current_hour = datetime.datetime.now().hour
current_minute = datetime.datetime.now().minute
current_second = datetime.datetime.now().second

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# print(f"{bcolors.HEADER}HEADER: No active frommets remain. Continue?{bcolors.ENDC}")
# print(f"{bcolors.OKBLUE}OKBLUE: No active frommets remain. Continue?{bcolors.ENDC}")
# print(f"{bcolors.OKCYAN}OKCYAN: No active frommets remain. Continue?{bcolors.ENDC}")
# print(f"{bcolors.OKGREEN}OKGREEN: No active frommets remain. Continue?{bcolors.ENDC}")
# print(f"{bcolors.WARNING}WARNING: No active frommets remain. Continue?{bcolors.ENDC}")
# print(f"{bcolors.FAIL}FAIL: No active frommets remain. Continue?{bcolors.ENDC}")
# print(f"{bcolors.ENDC}ENDC: No active frommets remain. Continue?{bcolors.ENDC}")
# print(f"{bcolors.BOLD}BOLD: No active frommets remain. Continue?{bcolors.ENDC}")
# print(f"{bcolors.UNDERLINE}UNDERLINE: No active frommets remain. Continue?{bcolors.ENDC}")


def querify(title):
  queryurl = "https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles="
  queryurl += urllib.parse.quote(title, safe='')
  queryurl += "&rvslots=*&rvprop=content&formatversion=2&format=json"
  return queryurl

def hiturl(url):
  response = requests.get(url, headers=headers)
  #print(queryurl)
  if response.status_code != 200:
    return(f"ERROR fetching text for {article['date']}/{article['subpage']}")
  else:
    try:
      # Parse that shizzle.
      bolus = json.loads(response.text)
      #print(bolus)
      return bolus["query"]["pages"][0]["revisions"][0]["slots"]["main"]["content"]
    except:
      print("Something was messed up on the page")
      print(bolus)
      exit()

def add_to_header(title, hed, sub, dry=True, auto=False, count=0):
  print(f"Adding subheading to {title}, {hed}: {sub}")
  text = hiturl(querify(title))
  #print(text)

  text = text.replace("<noinclude> {{Wikipedia:Signpost/Template:Signpost-header", "<noinclude>{{Wikipedia:Signpost/Template:Signpost-header")
  rsssub = f"{hed}: {sub}"
  rss = "<noinclude>{{Wikipedia:Wikipedia Signpost/Templates/RSS description|1=" + rsssub + "}}"
  header = "<noinclude>{{Wikipedia:Signpost/Template:Signpost-header"
  headerno = "{{Wikipedia:Signpost/Template:Signpost-header"
  if "Templates/RSS description" in text:
    print("ERROR: This already has a RSS header!")
    return count + 1
  if header in text:
    text = text.replace(header, headerno)
    textprint = bcolors.FAIL + rss + bcolors.ENDC + text
    text = rss + text
  else:
    textprint = bcolors.FAIL + rss + "</noinclude>" + bcolors.ENDC + text
    text = rss + "</noinclude>" + text


  if dry == False:
    for i in range(0, 10):
      print("")
    print(textprint[:2000])
    if auto == False:
      wait(f"Press any key to continue. Current count: {count}. x to exit, blank string to continue: ")
    uploader.upload_str(text, title, summary=f"Update article with metadata template for subheadings. Count: {str(count).zfill(4)}")
  else:
    for i in range(0, 10):
      print("")
    print(textprint[:2000])
    if auto == False:
      wait(f"DRY RUN: Press any key to continue. Current count: {count}. x to exit, blank string to continue: ")
    print(f"Dry run, not actually uploading. Current count: {count}. ")
  return count + 1

def wait(msg="x to exit, blank string to continue: "):

  ip = input(msg)
  if (ip == "x"):
    print("Aborting.")
    exit()
  return
  """
  if platform.system() == "Windows":
      os.system("pause")
  else:
      os.system(f"/bin/bash -c 'read -s -n 1 -p \"{msg}\"'")
  """

if (__name__ == "__main__"):

  f = open("test.txt", "r").read().split("\n")
  # Text file should be newline-separated list of pages.
  # Lines should look like:
  # "Wikipedia:Wikipedia_Signpost/2012-09-24".
  f = [n.strip() for n in f if n[0] != "#"]
  # Commented-out lines, beginning with #, will be ignored.
  
  # f = [urllib.parse.quote(n, safe='') for n in f]
  # print(f)

  count = 0
  for iss in range(0, len(f)):
    ftext = hiturl(querify(f[iss]))
    # Text = wikitext from API of the URL-formatted page title of the f element with index iss.
    w = mwparserfromhell.parse(ftext)
    ts = w.filter_templates()
    for t in ts:
      # print(str(t.name))
      if (str(t.name).strip() == "Signpost/item"):
        # print("title   = " + str(t.get("1").value))
        date = str(t.get("3").value)   
        dept = str(t.get("4").value)   
        hed = str(t.get("5").value)
        try:
          sub = str(t.get("sub").value)
          cprt = str(count).zfill(5)
          print(f"{cprt}: {date}, {dept}, {hed}: {sub}") 
          title = f"Wikipedia:{signpost}/{date}/{dept}"
          count = add_to_header(title, hed, sub, dry=False, auto=True, count=count)
        except Exception as err:
          print(f"ERROR! No subtitle for {date}/{dept}!")
          count += 1
        except SystemExit as err:
          # We are being passed a SystemExit from inside of add_to_header.
          exit()

























  ###############################################################################
  ###############################################################################
  ###############################################################################
  ###############################################################################
  ###############################################################################
  # Below this is nonsense.
  ###############################################################################
  ###############################################################################
  ###############################################################################
  ###############################################################################
  ###############################################################################