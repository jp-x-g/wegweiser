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
headers = weg_ver.headers()
# This is a secret tool that will come in handy later.
signpost = "Wikipedia Signpost"
current_year = int(datetime.datetime.now().year)
current_month = datetime.datetime.now().month
current_day = datetime.datetime.now().day

def fetch(year_start=current_year, year_end=current_year, month_range=13, mode="html", log_errors=False):
  # This technically takes a range of years as an argument, but for reasons,
  # it's only called for one at a time by the main method.


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
  
  if mode == "html":
    for year in all_articles:
      print(f"{year} ({len(all_articles[year])} articles) - beginning metadata retrieval.")
      for article in all_articles[year]:
        # print(article)
          obtained = obtain(article)
          article = obtained[0]
          errors += obtained[1]
  if mode == "hell":
    # This mode is called "hell" for a reason.
    # It would be straightforward, but I had to go be smart and batch it.
    # Now it's a disaster. It does run faster though.

    queryurls = []
    pagenames = []
    print("HAI!!!")
    # Since we're using the revisions API for this, we can batch our requests.
    for year in all_articles:
      print(f"{year} ({len(all_articles[year])} articles) - beginning metadata retrieval.")
      for article in all_articles[year]:
        pagename = "Wikipedia:" + signpost + "/" + article["date"] + "/" + article["subpage"]
        pagename = urllib.parse.quote(pagename, safe='')
        pagenames.append(pagename)

    # Now the batching part: we split the pagenames arrays into muiltiple-item subarrays to make greatest use of the Revisions API.
    # The API's limit is actually 500, but a URL with 500 full titles in it is far too long to be parsed, so we will do less.
    # Exhausting trials determined that: 8202 (eight two oh two) is the actual limit of how long a URL can be before it stops working.
    # 70 + 53 for the rest of the url params = 123, so of the 8079 remaining characters...
    # it divides into 255 only 31 times.
    # But really, when are page titles ACTUALLY 255 characters long?
    # Experimentally it seems to mostly work with 126 in a query.
    # Maybe we will compromise on 100 and call it a day.

    # Disregard that, the limit is 50 apparently (lol wut?)

    apilimit = 50
    subarrays = [pagenames[i:i + apilimit] for i in range(0, len(pagenames), apilimit)]
    # print(subarrays)
    print("len: " + str(len(subarrays)))
    for i in subarrays:
      batch = "|".join(i)
      queryurl = "https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=" + batch + "&rvslots=*&rvprop=content&formatversion=2&format=json"
      # print(queryurl)
      queryurls.append(queryurl)

    # We now have a big array of queryurls that we can hit and retrieve information from.
    # Note that the order will be more or less random when we actually get them back:
    # requesting the titles 1, 2, 3, 4, 5, 6, 7 will NOT return them as 1, 2, 3, 4, 5, 6, 7.
    # You get kind of a crazy-go-nuts stew of all of them in whatever order.

    article_stew = {}

    for url in queryurls:
      print(url)
      response = requests.get(url, headers=headers)
      if response.status_code != 200:
        print(f"ERROR getting views for {article['date']}/{article['subpage']}")
      else:
        # Parse that shizzle.
        bolus = json.loads(response.text)
        # print(bolus)
        for item in bolus["query"]["pages"]:
          text = item["revisions"][0]["slots"]["main"]["content"]
          title = item["title"]
          article_stew[title] = text
    # So now we've gone through every single query URL, retrieved the page text, and put them into a huge pile of slop.
    # Now we can go through and pick out individual 

    for year in all_articles:
      #for article in all_articles[year]:
      for a in range(0, len(all_articles[year])):
        pagename = "Wikipedia:" + signpost + "/" + all_articles[year][a]["date"] + "/" + all_articles[year][a]["subpage"]
          # Sound familiar? Yeah, it's because we have to fish the page back OUT OF THE STEW.
        if pagename in article_stew:
          # print("Happiness!")
          print(pagename)
          parsed = parse_hell(article_stew[pagename], all_articles[year][a]["date"], all_articles[year][a]["subpage"])
          all_articles[year][a] = parsed[0]
          errors += parsed[1]
        else:
          errors += f"\nCouldn't find title  : {pagename}"
          print(f"\nCouldn't find title  : {pagename}")

   # article = obtained[0]
   # errors += obtained[1]
  return(all_articles, errors)

def parse_hell(text, date, subpage):
  pagename = "Wikipedia:" + signpost + "/" + date + "/" + subpage
  datafields = {
          "date"      : date,
          "subpage"   : subpage,
          "title"     : "unparsed",
          "authors"   : ["unparsed"],
          "subheading": ""
          }
  errors = ""
  w = mwparserfromhell.parse(text)
  ts = w.filter_templates()
  for t in ts:
    # print(str(t.name))
    if (str(t.name).strip() == "Wikipedia:Wikipedia Signpost/Templates/Signpost-article-header-v2") or (str(t.name).strip() == "Wikipedia:Signpost/Template:Signpost-article-start"):
      # print("title   = " + str(t.get("1").value))
      hed = str(t.get("1").value)
      hed = hed.replace("\n", "").strip()
      if(hed[0:5]) == "{{{1|":
        hed = hed[5:]
      if(hed[-3:]) == "}}}":
        hed = hed[:-3]
      # Change "{{{1|Worthwhile Canadian Initiative}}}" to "Worthwhile Canadian Initiative".
      datafields["title"] = hed

      authors = str(t.get("2").value.strip_code())
      cln = clean_authors(str(authors), pagename)
      datafields["authors"] = cln[0]
      errors += cln[1]
      # print("authors = " + str(datafields["authors"]))
      if ("{{u" in str(t.get("2").value)) or ("{{U" in str(t.get("2").value)):
        errors += "\nTemplate:U for author: " + pagename

    elif str(t.name).strip() == "Wikipedia:Wikipedia Signpost/Templates/RSS description":
      #print("subhead = " + str(t.get("1").value))
      subhed = str(t.get("1").value)
      subhed = subhed.replace(str(datafields["title"]) + ": ", "")
      subhed = subhed.replace(str(datafields["title"]) + ":", "")
      subhed = subhed.replace(str(datafields["title"]), "")
      # This bewildering series of three lines fixes an occasional issue you see in some of the RSS description templates:
      # the article title will be included in them, and then the 
      datafields["subheading"] = subhed
  print(datafields)

  return(datafields, errors)

def clean_authors(authors, pagename="unspecified"):
  # At this point, if there are any authors at all...
  # the string will look like one of these:
  # "By Tom, Dick, and Harry"
  # "By Tom, Dick and Harry"
  # "By Tom, Dick & Harry"
  errors = ""
  try:
    if "\n" in authors:
      errors += f"\nLine break in author : {pagename}"
  
    if authors[:3] == "By ":
      authors = authors[3:]
    if authors[:3] == "by ":
      authors = authors[3:]
    # "Tom, Dick, and Harry"
    # "Tom, Dick and Harry"
    authors = authors.replace(" & ", ", ")
    # Consider having a username without ampersands in it.
    authors = authors.replace(", and", ", ")
    authors = authors.replace(" and ", ", ")
    # "Tom, Dick, Harry"
    authors = authors.split(", ")
    # We've now split it into an array:
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
    return(authors, errors)
  except Exception as err:
    print(f"BIG author error     : {err}")
    errors += f"\nBIG author error     : {pagename}"
    authors = "ERROR"
    return(authors, errors)

def obtain(article):

  errors = ""
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
        if i.has_attr("data-signpost-article-title"):
          # 2017 to present (2023)
          article["title"] = i["data-signpost-article-title"]
          print(f"Title: {article['title']}")
        else:
          # February 2017 and before.
          article["title"] = i.text
          print(f"Title: {article['title']}")
      except Exception as err:
        print(f"Title error: {err}")
        print(f"\nTitle error          : Wikipedia:Wikipedia Signpost/{article['date']}/{article['subpage']}")
        errors += f"\nTitle error          : Wikipedia:Wikipedia Signpost/{article['date']}/{article['subpage']}"
      if "\n" in article["title"]:
        print(f"\nLine break in title  : Wikipedia:Wikipedia Signpost/{article['date']}/{article['subpage']}")
        errors += f"\nLine break in title  : Wikipedia:Wikipedia Signpost/{article['date']}/{article['subpage']}"
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
      print(f"Author error         : {err}")
      errors += f"\nAuthor error         : Wikipedia:Wikipedia Signpost/{article['date']}/{article['subpage']}"
      authors = "none"
    if "\n" in authors:
      errors += f"\nLine break in author : Wikipedia:Wikipedia Signpost/{article['date']}/{article['subpage']}"
  
    cln = clean_authors(authors)
    article["authors"] = cln[0]
    errors += cln[1]
    print(f"Authors: {str(cln[0])}")
  
  return(article, errors)
  

def log(errors):
  datestamp = str(current_year) + "-" + str(current_month).zfill(2) + "-" + str(current_day).zfill(2)
  f = open("data/metadata-errors-" + datestamp + ".log", "w")
  f.write(errors)
  f.close()
  print("Written to " + "data/metadata-errors-" + save_name + ".log")

if (__name__ == "__main__"):

  current_year = int(datetime.datetime.now().year)

  month_range = 13
  year_start  = current_year
  year_end    = current_year
  # days        = 180
  
  ## Shorter values, for testing purposes
  # month_range = 7
  #year_start  = 2021
  #year_end    = 2022
  #days        = 180

  if len(sys.argv) > 1:
    if "-" in sys.argv[1]:
      year_start = int(sys.argv[1].split("-")[0])
      year_end   = int(sys.argv[1].split("-")[1])
    else:
      year_start = int(sys.argv[1])
      year_end   = int(sys.argv[1])
  
  if (year_start < 2005) or (year_end < 2005):
    print("ERROR: Years too early to exist.")
    print("The Signpost started on January 10, 2005!")
    exit()

  mode = "html"
  debug = False

  if ("-p" in sys.argv) or ("--parser" in sys.argv):
    mode = "hell"
  if ("-d" in sys.argv) or ("--debug" in sys.argv):
    debug = True


  all_errors = ""

  for i in range(year_start, year_end + 1):
    print(f"Saving to {i}")
    save_name = str(i) + "-metadata.txt"
    data = fetch(year_start=i, year_end=i, month_range=month_range, mode=mode)
    #print(json.dumps(data[0], indent=2))
    #exit()
    
    f = open("metadata/" + save_name, "w")
    f.write(json.dumps(data[0], indent=2))
    f.close()
    print("Written to " + "metadata/" + save_name)
    all_errors += str(data[1])
    if len(str(data[1])) == 0:
      print("No errors :^)")
    else:
      print("Errors: " + str(data[1]))

  if debug:
    log(all_errors)

  print("All years processed: " + str(year_start) + " to " + str(year_end) + "!")
  if len(all_errors) == 0:
    print("No errors :^)")
  else:
    print("Errors: " + all_errors)

  exit()
  