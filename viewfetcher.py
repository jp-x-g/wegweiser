# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys
# python -m pip install --upgrade luadata
import article_fetcher
import weg_ver
headers = weg_ver.headers()

# Normal usage looks like:
# python3 viewfetcher.py 2017
# or:
# python3 viewfetcher.py
# (returns for current year)


# This is a secret tool that will come in handy later.
signpost = "Wikipedia Signpost"


current_year = int(datetime.datetime.now().year)


month_range = 13
year_start  = current_year
year_end    = current_year
days        = 180

## Shorter values, for testing purposes
#month_range = 2
#year_start  = 2021
#year_end    = 2022
#days        = 180

if sys.argv[1]:
  year_start = int(sys.argv[1])
  year_end   = int(sys.argv[1])

save_name = str(year_start) + "-views.txt"

print(f"Saving to {save_name}")

views_no = "views" + str(days).zfill(3)

def extract_views(jsonners):
  jsonners = jsonners["items"]
  views = {}
  for the_range in [7, 15, 30, 60, 90, 120, 180]:
    view_no = "d" + str(the_range).zfill(3)
    # 7 becomes "d007"
    views[view_no] = -1
    if len(jsonners) < the_range:
      the_range = len(jsonners)
      # If the JSON only has 177 items, then just go to that.
    for i in range(0, the_range):
      #print(f'{i}: {jsonners[i]["views"]}')
      views[view_no] += jsonners[i]["views"]
      # Add, say, jsonners["items"][0] through jsonners["items"][6] to views["views007"].
  return views

def get_date_offset(date_str):
  # Parse the input string as a date
  date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
  two_days_before = date - datetime.timedelta(days=2)
  some_time_after = date + datetime.timedelta(days=days)
  # Return the two dates as strings
  return two_days_before.strftime("%Y%m%d00"), some_time_after.strftime("%Y%m%d00")

# Beautiful functions. Great! But we are not going to use them just yet.
# Before we can do anything, we need to get a darn list of all the articles.

###############################################################################
# Hits API (dodecice, normally) to get all articles published in the interval.
###############################################################################

all_articles = article_fetcher.fetch(year_start, year_end, month_range, format="dict")

###############################################################################
# All right, now we've got a skeleton dict with all of the issues in it.
###############################################################################

print(f"Retrieved {len(all_articles)} issues. Breakdown by year:")
for year in all_articles:
  print(f"{year}: {len(all_articles[year])}")
# print(json.dumps(all_articles, indent=2))

for year in all_articles:
  print(f"{year} ({len(all_articles[year])} articles) - beginning pageview retrieval.")
  for article in all_articles[year]:
    # Construct the API URL
    page_name = "Wikipedia:" + signpost + "/" + article["date"] + "/" + article["subpage"]
    page_name = urllib.parse.quote(page_name, safe='')
    start_date, end_date = get_date_offset(article["date"])
    # TODO: Make this customizable so you can see mobile, desktop, by country/region, etc
    # This information is already in the pageview stats, and might prove educative.
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{page_name}/daily/{start_date}/{end_date}"
    #     f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{page_name}/daily/{start_date}/{end_date}"
    #     (Old string; uses "all-agents" instead of "user", erroneously including automated hits in pageview totals)
    # See documentation at:
    #   https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews
    #   https://wikimedia.org/api/rest_v1/#/Pageviews%20data/get_metrics_pageviews_per_article__project___access___agent___article___granularity___start___end_
    #print(article)
    #print(article['subpage'])
    #print(f"Retrieving pageviews for {article['date']}/{article['subpage']}")
    print(url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      # print(f'Retrieved {url}')
      data = response.json()
      pageviews = extract_views(data)
      print(f"Retrieved pageviews for {article['date']}/{article['subpage']}: {pageviews}")
      article["views"] = pageviews
    else:
      print(f"ERROR getting views for {article['date']}/{article['subpage']}")
      

print(all_articles)

f = open("views/" + save_name, "w")
f.write(json.dumps(all_articles, indent=2))
f.close()

exit()