# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys
# python -m pip install --upgrade luadata

# Normal usage looks like:
# python3 viewfetcher.py 2017 180
# or:
# python3 viewfetcher.py 2017
# or:
# python3 viewfetcher.py
# (returns for current year)


headers = {"User-Agent": "JPxG's hoopty script (https://en.wikipedia.org/wiki/User:JPxG)"}

# This is a secret tool that will come in handy later.
signpost = "Wikipedia Signpost"

def fetch(year_start=int(datetime.datetime.now().year), year_end=int(datetime.datetime.now().year), month_range=13, format="dict"):
  page_list_array = []
  # All of the queries to send to the server and get a PrefixIndex-like list. Not returned.
  articles_array = []
  # Simple array of the pages, as they come from PrefixIndex.
  all_articles = {}
  # Formatted dict of all the pages, as they are in Module:Signpost.

  for year in range(year_start, (year_end + 1)):
    all_articles[str(year)] = []
    #for month in range(1, 13):
    for month in range(1, month_range):
      if month < 10:
        month = "0" + str(month)
      page_list_query = f"https://en.wikipedia.org/w/api.php?format=json&action=query&list=allpages&apprefix={signpost}%2F{year}-{month}&aplimit=max&apnamespace=4"
      month = int(month)
      # print(page_list_query)
      page_list_array.append(page_list_query)

  # Now we hit the API to populate the articles_array.
  for url in page_list_array:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      print(f'Retrieved {url}')
      data = response.json()
      for item in data["query"]["allpages"]:
        # print(item["title"])
        articles_array.append(item["title"])
    else:
      print(f'Error retrieving {url}')

  #print(articles_array)
  
  # Now we are going to mess with this array a little bit to try and make it more useful.
  # Right now we have this gigantic list of articles (ordered chronologically at least), but it's a mess.
  # Wouldn't it be nicer if the data were structured a little better?
  # For this, I am using the JSON formatting from Module:Signpost, which you can see at, for example:
  # https://en.wikipedia.org/wiki/Module:Signpost/Index/2022
  
  for article in articles_array:
    # Wikipedia:Wikipedia_Signpost/2022-08-01/Essay
    # 000000000011111111112222222222333333333344444444445
    # 012345678901234567890123456789012345678901234567890
    pref_len = len("Wikipedia:") + len(signpost) + len("/")
  
    issue_date = article[pref_len:(pref_len+10)]
    # 2022-08-01
    # 0123456789
    issue_y = issue_date[:4]
    issue_m = issue_date[5:7]
    issue_d = issue_date[8:]
    # pref_len plus eleven, to get just the article department
    article_dept = article[(pref_len+11):]
    # print(f"{issue_y} / {issue_m} / {issue_d} / {article_dept}")
    little_dict = {}
    little_dict["date"]    = issue_date
    little_dict["subpage"] = article_dept
    if (article_dept != "") and (article_dept != "SPV"):
      # No subpage name means it's the main page for that issue.
      # "SPV" is the old (2006esque) way that single issues were compiled
      #     (new ones are Wikipedia Signpost/Single/YYYY-MM-DD).
      all_articles[issue_y].append(little_dict)

  """
    # Old version, which organized them by issue. I think this is easier to work with...
    # But it doesn't gel with the formatting in Module:Signpost. Why reinvent the wheel?
    # If that ends up being irrelevant, maybe we can go back to this version.
    print(f"{issue_y} / {issue_m} / {issue_d} / {article_dept}")
    if issue_date not in all_articles[str(issue_y)]:
      all_articles[str(issue_y)][issue_date] = {}
    if article_dept != "":
      all_articles[str(issue_y)][issue_date][article_dept] = -1
  """
  if format == "array":
    return articles_array
  else:
    return all_articles