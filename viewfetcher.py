# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys
# python -m pip install --upgrade luadata
import article_fetcher

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


current_year = int(datetime.datetime.now().year)


month_range = 13
year_start  = current_year
year_end    = current_year
days        = 180

#month_range = 2
#year_start  = 2021
#year_end    = 2022
#days        = 180

if sys.argv[1]:
  year_start = int(sys.argv[1])
  year_end   = int(sys.argv[1])
  if len(sys.argv) > 2:
    days = int(sys.argv[2])

save_name = str(year_start) + "-" + str(days) + ".txt"

print(f"Saving to {save_name}")

views_no = "views" + str(days).zfill(3)

def extract_views(jsonners):
  views = 0
  for day in jsonners["items"]:
    views += int(day["views"])
    #print(day["views"])
  return views

def get_date_offset(date_str):
  # Parse the input string as a date
  date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
  two_days_before = date - datetime.timedelta(days=2)
  some_time_after = date + datetime.timedelta(days=(days - (3)))
  # The pageviews can only do daily for 180 days, so:
  # Two days before, one day before, the publication date, and 177 days after.
  # Or whatever the amount you're specifying is.
  # Return the two dates as strings
  return two_days_before.strftime("%Y%m%d00"), some_time_after.strftime("%Y%m%d00")

# Beautiful functions. Great! But we are not going to use them just yet.
# Before we can do anything, we need to get a darn list of all the articles.

# This builds a list of all query URLs to get every Signpost article.

all_articles = article_fetcher.fetch(year_start, year_end, month_range, days, format="dict")


# All right, now we've got a skeleton dict with all of the issues in it for the selected interval.
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
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{page_name}/daily/{start_date}/{end_date}"
    #print(url)
    #print(article)
    #print(article['subpage'])
    #print(f"Retrieving pageviews for {article['date']}/{article['subpage']}")
    #print(url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      # print(f'Retrieved {url}')
      data = response.json()
      pageviews = extract_views(data)
      print(f"Retrieved pageviews for {article['date']}/{article['subpage']}: {pageviews}")
      article[views_no] = int(pageviews)
    else:
      print(f"ERROR getting views for {article['date']}/{article['subpage']}")
      

print(all_articles)

f = open("views/" + save_name, "w")
f.write(json.dumps(all_articles, indent=2))
f.close()

exit()