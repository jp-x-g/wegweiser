# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys
# python -m pip install --upgrade luadata
import article_fetcher
from bs4 import BeautifulSoup
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
# month_range = 7
#year_start  = 2021
#year_end    = 2022
#days        = 180

if sys.argv[1]:
  year_start = int(sys.argv[1])
  year_end   = int(sys.argv[1])

save_name = str(year_start) + "-metadata.txt"

print(f"Saving to {save_name}")

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

errors = ""

for year in all_articles:
  print(f"{year} ({len(all_articles[year])} articles) - beginning metadata retrieval.")
  for article in all_articles[year]:

    article["title"] = "unparsed"
    article["authors"] = ["unparsed"]

    # Construct the API URL
    page_name = "Wikipedia:" + signpost + "/" + article["date"] + "/" + article["subpage"]
    page_name = urllib.parse.quote(page_name, safe='')
    #start_date, end_date = get_date_offset(article["date"])
    # TODO: Make this customizable so you can see mobile, desktop, by country/region, etc
    # This information is already in the pageview stats, and might prove educative.
    url = f"https://en.wikipedia.org/wiki/{page_name}"
    #print(f"Retrieving pageviews for {article['date']}/{article['subpage']}")
    #print(url)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
      print(f"ERROR getting views for {article['date']}/{article['subpage']}")
    else:
      # print(f'Retrieved {url}')
      soup = BeautifulSoup(response.text, 'html.parser')
      print(f"Retrieved {article['date']}/{article['subpage']} (length: {len(response.text)})")
      ########################################
      # Attempt to find the article title.
      ########################################
      titles = soup.find_all(id="signpost-article-title")
      #print(titles)
      for i in titles: 
        try:
          if i.has_key("data-signpost-article-title"):
            # 2017 to present (2023)
            article["title"] = i["data-signpost-article-title"]
            print(f"Title: {article['title']}")
          else:
            # February 2017 and before.
            article["title"] = i.text
            print(f"Title: {article['title']}")
        except Exception as err:
          print(f"Title error: {err}")
          errors += f"\nTitle error : Wikipedia:Wikipedia Signpost/{article['date']}/{article['subpage']}"

      ########################################
      # Attempt to find the authors. Tricky!
      ########################################
      authors = soup.find_all(id="signpost-article-authors")
      # Post-2017 author code.
      #print(f"all authors: {authors}")
      try:
        if len(authors) > 0:
          authors = authors[0].text
        else:
          # For pre-2017-02-27 issues, where it was "signpost-author"
          authors = soup.find_all(class_="signpost-author")
          authors = authors[0].text
      except Exception as err:
        print(f"Author error: {err}")
        errors += f"\nAuthor error: Wikipedia:Wikipedia Signpost/{article['date']}/{article['subpage']}"
        authors = "none"

      # At this point, if there are any authors at all...
      # the string will look like one of these:

      # "By Tom, Dick, and Harry"
      # "By Tom, Dick and Harry"
      # "By Tom, Dick & Harry"
      if authors[:3] == "By ":
        authors = authors[3:]
      # "Tom, Dick, and Harry"
      # "Tom, Dick and Harry"
      authors = authors.replace(" & ", ", ")
      # Consider having a username without ampersands in it.
      authors = authors.replace(", and", ", ")
      authors = authors.replace(" and ", ", ")
      # "Tom, Dick, Harry"
      authors = authors.split(", ")
      # ["Tom", "Dick", "Harry"]
      for i in range(0, len(authors)):
        if authors[i] == "":
          authors[i] = "none"
        else:
          # Clean out trailing spaces and gobbledygook.
          authors[i] = authors[i].replace("  ", " ")
          if authors[i][0] == " ":
            authors[i] = authors[i][1:]
          if authors[i][-1] == " ":
            authors[i] = authors[i][:-1]
          if authors[i][-1] == ".":
            authors[i] = authors[i][:-1]
      article["authors"] = authors
      print(f"Authors: {str(authors)}")


      

print(all_articles)

f = open("metadata/" + save_name, "w")
f.write(json.dumps(all_articles, indent=2))
f.close()

print(errors)

exit()