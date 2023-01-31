# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import sys

import lua_wrangler

headers = {"User-Agent": "JPxG's hoopty script (https://en.wikipedia.org/wiki/User:JPxG)"}

# This is a secret tool that will come in handy later.
signpost = "Wikipedia Signpost"

save_name = "2017-180.txt"

current_year = int(datetime.datetime.now().year)

month_range = 13
year_start  = 2017
year_end    = 2017
days        = 180

#month_range = 2
#year_start  = 2021
#year_end    = 2022
#days        = 180

if sys.argv[1]:
  year_start = int(sys.argv[1])
  year_end   = int(sys.argv[1])
  save_name  = str(sys.argv[1]) + "-180.txt"
  if sys.argv[2]:
    days = int(sys.argv[2])
    save_name  = str(sys.argv[1]) + "-" + str(sys.argv[2]) + ".txt"

print(f"Saving to {save_name}")

views_no    = "views" + str(days)


def extract_views(jsonners):
  views = 0
  for day in jsonners["items"]:
    views += int(day["views"])
    #print(day["views"])
  return views

# "The following is a Python script that takes a text string in the form "yyyy-mm-dd" and returns two strings: the date two days before, and the date five months after."
def get_date_offset(date_str):
  # Parse the input string as a date
  date = datetime.datetime.strptime(date_str, "%Y-%m-%d")

  # Calculate the date two days before
  two_days_before = date - datetime.timedelta(days=2)

  # Calculate the date five months after
  some_time_after = date + datetime.timedelta(days=(days - (3)))

  # The pageviews can only do daily for 180 days, so:
  # Two days before, one day before, the publication date, and 177 days after.
  # Or whatever the amount you're specifying is.

  # Return the two dates as strings
  return two_days_before.strftime("%Y%m%d00"), some_time_after.strftime("%Y%m%d00")

# Beautiful functions. Great! But we are not going to use them just yet.
# Before we can do anything, we need to get a darn list of all the articles.

# This builds a list of all query URLs to get every Signpost article from 2005 to the hither.

page_list_array = []
all_articles = {}

#for year in range(2005, current_year + 1):
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
print(page_list_array)

print(all_articles)

articles_array = []

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
  little_dict["views"]   = -1
  if article_dept != "":
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
      article["views"] = int(pageviews)
    else:
      print(f"ERROR getting views for {article['date']}/{article['subpage']}")
      

print(all_articles)

f = open(save_name, "w")
f.write(json.dumps(all_articles, indent=2))
f.close()

exit()
indytwo = [
  {
    "date" : "2022-01-30",
    "subpage" : "Arbitration report",
    "title" : "New arbitrators look at new case and antediluvian sanctions",
    "tags" : {"arbitrationreport"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Black History Month",
    "title" : "What are you doing for Black History Month?",
    "tags" : {"bias"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Crossword",
    "title" : "Cross swords with a crossword",
    "tags" : {},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Deletion report",
    "title" : "Ringing in the new year: Subject notability guideline under discussion",
    "tags" : {"afd"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Essay",
    "title" : "The prime directive",
    "tags" : {"essay"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Gallery",
    "title" : "No Spanish municipality without a photograph",
    "tags" : {"gallery"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "In the media",
    "title" : "Fuzzy-headed government editing",
    "tags" : {"inthemedia", "paidadvocacy"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Interview",
    "title" : "CEO Maryana Iskander \"four weeks in\"",
    "tags" : {"foundation", "interviews", "maryanaiskander"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "News and notes",
    "title" : "Feedback for Board of Trustees election",
    "tags" : {"administrator", "board", "chinesewikipedia", "foundation", "newsandnotes"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Obituary",
    "title" : "Twofingered Typist",
    "tags" : {},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Op-Ed",
    "title" : "Identifying and rooting out climate change denial",
    "tags" : {"opinion"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Opinion",
    "title" : "Should the Wikimedia Foundation continue to accept cryptocurrency donations?",
    "tags" : {"foundation", "opinion"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Recent research",
    "title" : "Articles with higher quality ratings have fewer \"knowledge gaps\"",
    "tags" : {"goodarticles", "recentresearch", "research"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Serendipity",
    "title" : "Pooh entered the Public Domain – but Tigger has to wait two more years",
    "tags" : {},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Special report",
    "title" : "WikiEd course leads to Twitter harassment",
    "tags" : {"education", "specialreport"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "Traffic report",
    "title" : "The most viewed articles of 2021",
    "tags" : {"statistics", "traffic", "trafficreport"},
  },
  {
    "date" : "2022-01-30",
    "subpage" : "WikiProject report",
    "title" : "The Forgotten Featured",
    "tags" : {"articleassessment", "wikiprojectreport", "wikiprojects"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Arbitration report",
    "title" : "Parties remonstrate, arbs contemplate, skeptics coordinate",
    "tags" : {"arbitrationreport"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "By the numbers",
    "title" : "Does birthplace affect the frequency of Wikipedia biography articles?",
    "tags" : {"biography", "frenchwikipedia"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Crossword",
    "title" : "A Crossword, featuring Featured Articles",
    "tags" : {"crossword"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Deletion report",
    "title" : "The 10 most SHOCKING deletion discussions of February",
    "tags" : {"afd"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Featured content",
    "title" : "Featured Content returns",
    "tags" : {"featuredcontent"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "From the team",
    "title" : "Selection of a new Signpost Editor-in-Chief",
    "tags" : {"fromtheeditor"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Gallery",
    "title" : "The vintage exhibit",
    "tags" : {"gallery"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Humour",
    "title" : "Notability of mailboxes",
    "tags" : {"humour"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "In the media",
    "title" : "Wiki-drama in the UK House of Commons",
    "tags" : {"coi", "foundation", "inthemedia"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "News and notes",
    "title" : "Impacts of Russian invasion of Ukraine",
    "tags" : {"newsandnotes"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "News from Diff",
    "title" : "The Wikimania 2022 Core Organizing Team",
    "tags" : {"foundation"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Opinion",
    "title" : "Why student editors are good for Wikipedia",
    "tags" : {"education", "opinion"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Recent research",
    "title" : "How editors and readers may be emotionally affected by disasters and terrorist attacks",
    "tags" : {"recentresearch", "research"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Serendipity",
    "title" : "War photographers: from Crimea (1850s) to the Russian invasion of Ukraine (2022)",
    "tags" : {"gallery"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Special report",
    "title" : "A presidential candidate's team takes on Wikipedia",
    "tags" : {"coi", "frenchwikipedia", "specialreport"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Technology report",
    "title" : "Community Wishlist Survey results",
    "tags" : {"foundation", "tech", "technologyreport"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "Traffic report",
    "title" : "Euphoria, Pamela Anderson, lies and Netflix",
    "tags" : {"statistics", "traffic", "trafficreport"},
  },
  {
    "date" : "2022-02-27",
    "subpage" : "WikiProject report",
    "title" : "10 years of tea",
    "tags" : {"wikiprojectreport", "wikiprojects"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Arbitration report",
    "title" : "Skeptics given heavenly judgement, whirlwind of Discord drama begins to spin for tropical cyclone editors",
    "tags" : {"arbcom", "arbitrationreport"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Deletion report",
    "title" : "Ukraine, werewolves, Ukraine, YouTube pundits, and Ukraine",
    "tags" : {"mfd", "russia", "ukraine"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Discussion report",
    "title" : "Athletes are less notable now",
    "tags" : {"discussionreport", "mfd", "nsport", "ukraine", "universalcodeofconduct"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Disinformation report",
    "title" : "The oligarchs' socks",
    "tags" : {"coi", "paidadvocacy", "russia"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Essay",
    "title" : "Yes, the sky is blue",
    "tags" : {"essay", "verifiability"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Eyewitness Wikimedian – Kharkiv, Ukraine",
    "title" : "Countering Russian aggression with a camera",
    "tags" : {"opinion", "russia", "ukraine"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Eyewitness Wikimedian – Vinnytsia, Ukraine",
    "title" : "War diary",
    "tags" : {"opinion", "russia", "ukraine"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Eyewitness Wikimedian – Western Ukraine",
    "title" : "Working with Wikipedia helps",
    "tags" : {"opinion", "russia", "ukraine"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "From the archives",
    "title" : "Burn, baby burn",
    "tags" : {"backup", "fromthearchives"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "From the Signpost team",
    "title" : "We stand in solidarity with Ukraine",
    "tags" : {"fromtheeditor", "ukraine"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Gallery",
    "title" : "\"All we are saying is, give peace a chance...\"",
    "tags" : {"gallery", "russia", "ukraine"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "In the media",
    "title" : "Ukraine, Russia, and even some other stuff",
    "tags" : {"inthemedia", "russia", "russianwikipedia", "ukraine", "ukrainianwikipedia"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "News and notes",
    "title" : "Of safety and anonymity",
    "tags" : {"jimmywales", "newsandnotes", "russia", "russianwikipedia", "ukraine", "universalcodeofconduct"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "On the bright side",
    "title" : "The bright side of news",
    "tags" : {"poland", "russia", "ukraine"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Recent research",
    "title" : "Top scholarly citers, lack of open access references, predicting editor departures",
    "tags" : {"chinesewikipedia", "openaccess", "recentresearch", "research", "wikidata"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Technology report",
    "title" : "2022 Wikimedia Hackathon",
    "tags" : {"bot", "foundation", "hackathon", "script", "tech", "technologyreport", "vector2022"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Tips and tricks",
    "title" : "Become a keyboard ninja",
    "tags" : {"mediawiki", "regex", "wiktionary"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Traffic report",
    "title" : "War, what is it good for?",
    "tags" : {"russia", "statistics", "traffic", "trafficreport", "ukraine"},
  },
  {
    "date" : "2022-03-27",
    "subpage" : "Wikimedian perspective",
    "title" : "My heroes from Russia, Ukraine & beyond",
    "tags" : {"gallery", "russia", "ukraine"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Essay",
    "title" : "The problem with elegant variation",
    "tags" : {"essay", "synonyms"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Eyewitness Wikimedian – Vinnytsia, Ukraine",
    "title" : "War diary (Part 2)",
    "tags" : {"ukraine"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Featured content",
    "title" : "Wikipedia's best content from March",
    "tags" : {"featuredcontent", "gallery"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "From the archives",
    "title" : "Wales resigned WMF board chair in 2006 reorganization",
    "tags" : {"board", "chair", "fromthearchives", "jimbo", "moller"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Gallery",
    "title" : "A voyage around the world with WLM winners",
    "tags" : {"gallery", "wikilovesmonuments", "wikimediacommons"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Humour",
    "title" : "Really huge message boxes",
    "tags" : {"humour"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "In focus",
    "title" : "Editing difficulties on Russian Wikipedia",
    "tags" : {"infocus", "russianwikipedia", "ukraine"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "In the media",
    "title" : "The battlegrounds outside and inside Wikipedia",
    "tags" : {"coi", "disinformation", "germanwikipedia", "inthemedia"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Interview",
    "title" : "On a war and a map",
    "tags" : {"interviews", "ukraine", "wikimediacommons"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "News and notes",
    "title" : "Double trouble",
    "tags" : {"backlog", "belarus", "board", "foundation", "newsandnotes", "ombuds", "universalcodeofconduct", "vector", "wikilovesafrica"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "News from the WMF",
    "title" : "How Smart is the SMART Copyright Act?",
    "tags" : {"dmca", "licensing", "newsfromthewmf"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Recent research",
    "title" : "Student edits as \"civic engagement\"; how Wikipedia readers interact with images",
    "tags" : {"recentresearch", "research"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Serendipity",
    "title" : "Wikipedia loves photographs, but hates photographers",
    "tags" : {"cc", "wikimediacommons"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Special report",
    "title" : "Ukrainian Wikimedians during the war",
    "tags" : {"specialreport", "ukraine", "ukrainianwikipedia"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Technology report",
    "title" : "8-year-old attribution issues in Media Viewer",
    "tags" : {"bot", "foundation", "mediaviewer", "tech", "technologyreport"},
  },
  {
    "date" : "2022-04-24",
    "subpage" : "Traffic report",
    "title" : "Justice Jackson, the Smiths, and an invasion",
    "tags" : {"statistics", "traffic", "trafficreport"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Community view",
    "title" : "Have your say in the 2022 Wikimedia Foundation Board elections",
    "tags" : {"board", "communityview"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Discussion report",
    "title" : "Portals, April Fools, admin activity requirements and more",
    "tags" : {"adminship", "discussionreport", "outing", "rfc"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Essay",
    "title" : "How not to write a Wikipedia article",
    "tags" : {"essay"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Featured content",
    "title" : "Featured content of April",
    "tags" : {"featuredcontent"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "From the archives",
    "title" : "The Onion and Wikipedia",
    "tags" : {"fromthearchives"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "From the team",
    "title" : "A changing of the guard",
    "tags" : {"fromtheeditor"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Gallery",
    "title" : "Diving under the sea for World Oceans Day",
    "tags" : {"gallery", "ocean"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Humour",
    "title" : "A new crossword",
    "tags" : {"crossword", "humour"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "In focus",
    "title" : "Measuring gender diversity in Wikipedia articles",
    "tags" : {"diversity", "frenchwikipedia", "infocus", "lgbt"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "In the media",
    "title" : "Putin, Jimbo, Musk and more",
    "tags" : {"coi", "inthemedia", "jimmywales", "russia", "russianwikipedia", "ukraine"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Interview",
    "title" : "Wikipedia's Pride",
    "tags" : {"interviews", "lgbt"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "News and notes",
    "title" : "2022 Wikimedia Board elections",
    "tags" : {"adminship", "board", "finance", "newsandnotes", "universalcodeofconduct"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "News from Diff",
    "title" : "Winners of the Human rights and Environment special nomination by Wiki Loves Earth announced",
    "tags" : {"gallery", "wikilovesearth"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "News from the WMF",
    "title" : "The EU Digital Services Act: What’s the Deal with the Deal?",
    "tags" : {"foundation", "licensing", "newsfromthewmf"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Opinion",
    "title" : "The Wikimedia Endowment – a lack of transparency",
    "tags" : {"finance", "opinion"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Recent research",
    "title" : "35 million Twitter links analysed",
    "tags" : {"recentresearch", "research"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Serendipity",
    "title" : "Those thieving image farms",
    "tags" : {"licensing", "wikimediacommons"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Special report",
    "title" : "Three stories of Ukrainian Wikimedians during the war",
    "tags" : {"specialreport", "ukraine", "ukrainianwikipedia"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Technology report",
    "title" : "A new video player for Wikimedia wikis",
    "tags" : {"bot", "hackathon", "script", "tech", "technologyreport"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Tips and tricks",
    "title" : "The reference desks of Wikipedia",
    "tags" : {"teahouse", "villagepump"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Traffic report",
    "title" : "Strange highs and strange lows",
    "tags" : {"statistics", "traffic", "trafficreport"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "Video",
    "title" : "How the entire country of Qatar was blocked from editing",
    "tags" : {"qatar", "vandalism"},
  },
  {
    "date" : "2022-05-29",
    "subpage" : "WikiProject report",
    "title" : "WikiProject COVID-19 revisited",
    "tags" : {"covid", "wikiprojectreport", "wikiprojects"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Discussion report",
    "title" : "MoS rules on CCP name mulled, XRV axe plea nulled, mass drafting bid pulled",
    "tags" : {"blp", "china", "discussionreport", "manualofstyle", "xrv"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Essay",
    "title" : "RfA trend line haruspicy: fact or fancy?",
    "tags" : {"adminship", "essay"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Featured content",
    "title" : "Articles on Scots' clash, Yank's tux, Austrian's action flick deemed brilliant prose",
    "tags" : {"featuredcontent"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Gallery",
    "title" : "Celebration of summer, winter",
    "tags" : {"gallery"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Humour",
    "title" : "Shortcuts, screwballers, Simon & Garfunkel",
    "tags" : {"crossword", "humour"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "In the media",
    "title" : "Editor given three-year sentence, big RfA makes news, Guy Standing takes it sitting down",
    "tags" : {"adminship", "coi", "inthemedia", "russianwikipedia", "ukraine"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "News and notes",
    "title" : "WMF inks new rules on government-ordered takedowns, blasts Russian feds' censor demands, spends big bucks",
    "tags" : {"finance", "foundation", "newsandnotes", "russianwikipedia", "ukraine"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "News from the WMF",
    "title" : "Wikimedia Enterprise signs first deals",
    "tags" : {"foundation", "newsfromthewmf"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Opinion",
    "title" : "Picture of the Day – how Adam plans to ru(i)n it",
    "tags" : {"gallery", "opinion", "pictureoftheday"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Recent research",
    "title" : "Wikipedia versus academia (again), tables' \"immortality\" probed",
    "tags" : {"recentresearch", "research"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Serendipity",
    "title" : "Was she really a Swiss lesbian automobile racer?",
    "tags" : {"dutchwikipedia", "germanwikipedia"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Special report",
    "title" : "\"Wikipedia's independence\" or \"Wikimedia's pile of dosh\"?",
    "tags" : {"finance", "foundation", "specialreport"},
  },
  {
    "date" : "2022-06-26",
    "subpage" : "Traffic report",
    "title" : "Top view counts for shows, movies, and celeb lawsuit that keeps on giving",
    "tags" : {"statistics", "traffic", "trafficreport"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Arbitration report",
    "title" : "Winds of change blow for cyclone editors, deletion dustup draws toward denouement",
    "tags" : {"arbitrationreport", "xfd"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Community view",
    "title" : "Youth culture and notability",
    "tags" : {"communityview", "notability"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Deletion report",
    "title" : "This is Gonzo Country",
    "tags" : {"afd"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Discussion report",
    "title" : "Notability for train stations, notices for mobile editors, noticeboards for the rest of us",
    "tags" : {"adminship", "afd", "discussionreport", "notability"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Election guide",
    "title" : "The chosen six: 2022 Wikimedia Foundation Board of Trustees elections",
    "tags" : {"board"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Essay",
    "title" : "How to research an image",
    "tags" : {"essay"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Eyewitness Wikimedian – Vinnytsia, Ukraine",
    "title" : "War diary (part 3)",
    "tags" : {"ukraine"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Featured content",
    "title" : "A little list with surprisingly few lists",
    "tags" : {"featuredcontent"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "From the archives",
    "title" : "2012 Russian Wikipedia shutdown as it happened",
    "tags" : {"fromthearchives", "russianwikipedia"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "From the editors",
    "title" : "Rise of the machines, or something",
    "tags" : {"fromtheeditor"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Gallery",
    "title" : "A backstage pass",
    "tags" : {"gallery"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Humour",
    "title" : "Why did the chicken cross the road?",
    "tags" : {"humour"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "In focus",
    "title" : "Wikidata insights from a handy little tool",
    "tags" : {"infocus", "wikidata"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "In the media",
    "title" : "Censorship, medieval hoaxes, \"pathetic supervillains\", FB-WMF AI TL bid, dirty duchess deeds done dirt cheap",
    "tags" : {"afd", "censorship", "chinesewikipedia", "coi", "hoax", "inthemedia", "lgbt", "lta", "maryanaiskander", "russianwikipedia"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "News and notes",
    "title" : "Information considered harmful",
    "tags" : {"ecosoc", "foundation", "meta", "newsandnotes", "russia", "russianwikipedia", "ukraine", "universalcodeofconduct", "wipo"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "On the bright side",
    "title" : "Ukrainian Wikimedians during the war — three (more) stories",
    "tags" : {"ukraine", "ukrainianwikipedia"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Op-Ed",
    "title" : "The \"recession\" affair",
    "tags" : {"opinion", "politics", "protection"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Opinion",
    "title" : "Criminals among us",
    "tags" : {"coi", "opinion"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Recent research",
    "title" : "A century of rulemaking on Wikipedia analyzed",
    "tags" : {"recentresearch", "research"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Serendipity",
    "title" : "Don't cite Wikipedia",
    "tags" : {"gallery", "wikimediacommons", "wikipedia"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Tips and tricks",
    "title" : "Cleaning up awful citations with Citation bot",
    "tags" : {"bot", "citations"},
  },
  {
    "date" : "2022-08-01",
    "subpage" : "Traffic report",
    "title" : "US TV, JP ex-PM, outer space, and politics of IN, US, UK top charts for July",
    "tags" : {"statistics", "traffic", "trafficreport"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Discussion report",
    "title" : "SubscribeBoarding the Trustees",
    "tags" : {"board", "discussionreport"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Essay",
    "title" : "Delete the junk!",
    "tags" : {"afd", "essay", "votesfordeletion"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Featured content",
    "title" : "Our man drills are safe for work, but our Labia is Fausta.",
    "tags" : {"featuredcontent"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "From the archives",
    "title" : "5, 10, and 15 years ago",
    "tags" : {"foundation", "fromthearchives", "licensing", "swedishwikipedia", "wikimediacommons"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Gallery",
    "title" : "SubscribeA Fringe Affair (but not the show by Edward W. Feery that was on this year)",
    "tags" : {"gallery"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Humour",
    "title" : "CommonsComix No. 1",
    "tags" : {"editwars", "humour", "wikimediacommons"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "In focus",
    "title" : "Thinking inside the box",
    "tags" : {"infocus", "userbox"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "In the media",
    "title" : "Truth or consequences? A tough month for truth",
    "tags" : {"coi", "finance", "hoax", "inthemedia", "jimmywales", "maryanaiskander", "paid", "russia", "ukraine"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "News and notes",
    "title" : "Admins wanted on English Wikipedia, IP editors not wanted on Farsi Wiki, donations wanted everywhere",
    "tags" : {"adminship", "finance", "ip", "newsandnotes", "persianwikipedia"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "News from Wiki Education",
    "title" : "18 years a Wikipedian: what it means to me",
    "tags" : {"education", "wikied"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Recent research",
    "title" : "The dollar value of \"official\" external links",
    "tags" : {"recentresearch", "research"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Serendipity",
    "title" : "Two photos of every library on earth",
    "tags" : {"library", "wikimediacommons"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Special report",
    "title" : "Wikimania 2022: no show, no show up?",
    "tags" : {"specialreport", "wikimania"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Technology report",
    "title" : "SubscribeVector (2022) deployment discussions happening now",
    "tags" : {"bot", "tech", "technologyreport", "vector", "wikimediacommons"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Tips and tricks",
    "title" : "The unexpected rabbit hole of typo fixing in citations...",
    "tags" : {"citation", "typo"},
  },
  {
    "date" : "2022-08-31",
    "subpage" : "Traffic report",
    "title" : "SubscribeWhat dreams (and heavily trafficked articles) may come",
    "tags" : {"statistics", "traffic", "trafficreport"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "CommonsComix",
    "title" : "CommonsComix 2: Paulus Moreelse",
    "tags" : {"humour"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "Discussion report",
    "title" : "Much ado about Fox News",
    "tags" : {"discussionreport", "foxnews", "newpagepatrol", "reliablesourcesnoticeboard"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "Featured content",
    "title" : "Farm-fresh content",
    "tags" : {"featuredcontent"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "From the archives",
    "title" : "5, 10, and 15 Years ago: September 2022",
    "tags" : {"fromthearchives"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "Gallery",
    "title" : "A Festival Descends on the City: The Edinburgh Fringe, Pt. 2",
    "tags" : {"gallery"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "In focus",
    "title" : "NPP: Still heaven or hell for new users – and for the reviewers",
    "tags" : {"finance", "foundation", "infocus", "maryanaiskander", "newpagepatrol"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "In the media",
    "title" : "A few complaints and mild disagreements",
    "tags" : {"coi", "inthemedia", "katherinemaher", "npov", "russianwikipedia"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "Interview",
    "title" : "ScottishFinnishRadish's Request for Adminship",
    "tags" : {"adminship", "interviews"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "News and notes",
    "title" : "Board vote results, bot's big GET, crat chat gives new mop, WMF seeks \"sound logo\" and \"organizer lab\"",
    "tags" : {"adminship", "board", "foundation", "newsandnotes", "universalcodeofconduct"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "Opinion",
    "title" : "Are we ever going to reach consensus?",
    "tags" : {"afd", "opinion"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "Recent research",
    "title" : "How readers assess Wikipedia's trustworthiness, and how they could in the future",
    "tags" : {"finance", "recentresearch", "research"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "Serendipity",
    "title" : "Removing watermarks, copyright signs and cigarettes from photos",
    "tags" : {"cc", "wikimediacommons"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "Special report",
    "title" : "Decentralized Fundraising, Centralized Distribution",
    "tags" : {"finance", "germanwikipedia", "specialreport"},
  },
  {
    "date" : "2022-09-30",
    "subpage" : "Traffic report",
    "title" : "Kings and queens and VIPs",
    "tags" : {"statistics", "traffic", "trafficreport"},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "Disinformation report",
    "title" : "From Russia with WikiLove",
    "tags" : {},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "Featured content",
    "title" : "Topics, lists, submarines and Gurl.com",
    "tags" : {"featuredcontent"},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "From the archives",
    "title" : "Paid advocacy, a lawsuit over spelling mistakes, deleting Jimbo's article, and the death of Toolserver",
    "tags" : {"fromthearchives"},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "From the team",
    "title" : "A new goose on the roost",
    "tags" : {"fromtheteam"},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "In the media",
    "title" : "Scribing, searching, soliciting, spying, and systemic bias",
    "tags" : {"inthemedia"},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "Interview",
    "title" : "Isabelle Belato on their Request for Adminship",
    "tags" : {"interviews"},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "News and notes",
    "title" : "Wikipedians question Wikimedia fundraising ethics after \"somewhat-viral\" tweet",
    "tags" : {"finance", "lisaseitzgruwell", "maryanaiskander", "newsandnotes"},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "News from the WMF",
    "title" : "Governance updates from, and for, the Wikimedia Endowment",
    "tags" : {"newsfromthewmf"},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "Recent research",
    "title" : "Disinformatsiya: Much research, but what will actually help Wikipedia editors?",
    "tags" : {"recentresearch", "research"},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "Serendipity",
    "title" : "We all make mistakes – don’t we?",
    "tags" : {},
  },
  {
    "date" : "2022-10-31",
    "subpage" : "Traffic report",
    "title" : "Mama, they're in love with a criminal",
    "tags" : {"statistics", "traffic", "trafficreport"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Book review",
    "title" : "''Writing the Revolution''",
    "authors" : {"Jayen466"},
    "tags" : {"bookreview", "revolution", "wikipedia"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "CommonsComix",
    "title" : "Joker's trick",
    "authors" : {"Adam Cuerden"},
    "tags" : {"hoax", "humour", "wikimediacommons"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Concept",
    "title" : "The relevance of legal certainty to the English Wikipedia",
    "authors" : {},
    "tags" : {"adminship", "concept", "wikipedia"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Disinformation report",
    "title" : "Missed and Dissed",
    "authors" : {"JPxG", "Smallbones", "Adam Cuerden"},
    "tags" : {"disinformation"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Essay",
    "title" : "The Six Million FP Man",
    "authors" : {"Adam Cuerden"},
    "tags" : {"essay", "featuredpicture", "wikimediacommons"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Featured content",
    "title" : "A great month for featured articles",
    "authors" : {"Adam Cuerden"},
    "tags" : {"featuredcontent"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "From the archives",
    "title" : "Five, ten, and fifteen years ago",
    "authors" : {"Adam Cuerden", "HaeB"},
    "tags" : {"fromthearchives", "jimmywales", "otrs"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "In the media",
    "title" : "\"The most beautiful story on the Internet\"",
    "authors" : {"Bluerasberry", "Bri", "JPxG", "Smallbones"},
    "tags" : {"cryptocurrency", "finance", "foundation", "inthemedia", "vpn", "wikipedia"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Interview",
    "title" : "Lisa Seitz-Gruwell on WMF fundraising in the wake of big banner ad RfC",
    "authors" : {"The Land", "Lgruwell-WMF"},
    "tags" : {"finance", "foundation", "interviews", "lisaseitzgruwell"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "News and notes",
    "title" : "English Wikipedia editors: \"We don't need no stinking banners\"",
    "authors" : {"Adam Cuerden", "Jayen466", "Bri", "Helloheart"},
    "tags" : {"finance", "maryanaiskander", "newsandnotes"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Obituary",
    "title" : "A tribute to Michael Gäbler",
    "authors" : {"Rhododendrites", "Matthew (WMF)", "Adam Cuerden"},
    "tags" : {"obit", "wikimediacommons"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Op-Ed",
    "title" : "Diminishing returns for article quality",
    "authors" : {"Julle"},
    "tags" : {"opinion", "wikipedia"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Opinion",
    "title" : "Privacy on Wikipedia in the cyberpunk future",
    "authors" : {"Ladsgroup"},
    "tags" : {"opinion", "persianwikipedia", "spi"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Recent research",
    "title" : "Study deems COVID-19 editors smart and cool, questions of clarity and utility for WMF's proposed \"Knowledge Integrity Risk Observatory\"",
    "authors" : {"Piotrus", "HaeB"},
    "tags" : {"covid", "croatianwikipedia", "foundation", "recentresearch", "research"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Technology report",
    "title" : "Galactic dreams, encyclopedic reality",
    "authors" : {"JPxG", "Adam Cuerden", "Bri", "Smallbones"},
    "tags" : {"ai", "galactica", "tech", "technologyreport"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Tips and tricks",
    "title" : "(Wiki)break stuff",
    "authors" : {"Headbomb"},
    "tags" : {"wikibreak", "wikipediholism"},
  },
  {
    "date" : "2022-11-28",
    "subpage" : "Traffic report",
    "title" : "Musical deaths, murders, Princess Di's nominative determinism, and sports",
    "authors" : {"Igordebraga", "YttriumShrew", "SSSB"},
    "tags" : ["statistics", "traffic", "trafficreport"],
  }]
#print(indytwo[0])

# TODO: Come up with some way to gracefully parse in the module indices. This is horrific.

indexyear = 2022

for index in range(0, len(indytwo)):
  # print("Mod item is this: ", indytwo[index])
  for my_item in all_articles[str(indexyear)]:
    #print("My item is this: ", my_item)
    if (my_item["date"] == indytwo[index]["date"]) and (my_item["subpage"] == indytwo[index]["subpage"]):
      print("Wow found it!!!!!!!!")
      indytwo[index][views_no] = my_item["views"]

#TODO: whatever
#output = {"2022": indytwo}
#output = json.dumps(output, indent=2)

output = str(indytwo)
print(output)

# Now for the truly hoopty nonsense.

print(output)
f = open("indytwo.txt", "w")
f.write(str(output))
f.close()

outputtwo = lua_wrangler.luaify(indytwo)

print(outputtwo)

f = open("indythree.txt", "w")
f.write(str(outputtwo))
f.close()
