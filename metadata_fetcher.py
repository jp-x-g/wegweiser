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
current_hour = datetime.datetime.now().hour
current_minute = datetime.datetime.now().minute
current_second = datetime.datetime.now().second

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
          "subhead": ""          
          }

  errors = ""
  w = mwparserfromhell.parse(text)
  ts = w.filter_templates()
  for t in ts:
    # print(str(t.name))
    if (str(t.name).strip() == "Wikipedia:Wikipedia Signpost/Templates/Signpost-article-header-v2") or (str(t.name).strip() == "Wikipedia:Signpost/Template:Signpost-article-start"):
      # print("title   = " + str(t.get("1").value))
      hed = str(t.get("1").value)
      if "\t" in hed:
        errors += "\nTab char in headline : " + pagename
      hed = dewhiten(hed)
      if(hed[0:5]) == "{{{1|":
        hed = hed[5:]
      if(hed[-3:]) == "}}}":
        hed = hed[:-3]
      # Change "{{{1|Worthwhile Canadian Initiative}}}" to "Worthwhile Canadian Initiative".
      datafields["title"] = dewhiten(hed)

      authors = str(t.get("2").value.strip_code())
      cln = clean_authors(str(authors), pagename)
      datafields["authors"] = cln[0]
      errors += cln[1]
      # print("authors = " + str(datafields["authors"]))
      if ("{{u" in str(t.get("2").value)) or ("{{U" in str(t.get("2").value)):
        errors += "\nTemplate:U for author: " + pagename
      # TODO: Write something to parse out all of the weird userlink templates:
      # {{u|asdf}}, {{U|asdf}}, {{ul|asdf}}, {{noping|asdf}}, {{np|asdf}}

    elif str(t.name).strip() == "Wikipedia:Wikipedia Signpost/Templates/RSS description":
      #print("subhead = " + str(t.get("1").value))
      subhed = str(t.get("1").value)
      datafields["subhead"] = subhed


  # Clean out subheading.

  # An occasional issue you get using RSS templates for subheadings is that...
  # sometimes the article title will be included in them before the subhead.

  sh = dewhiten(str(datafields["subhead"]))
  ti = dewhiten(str(datafields["title"]))

  if (ti in sh):
    if (sh.find(ti) == 0):
      sh = sh.replace(ti + ": ", "")
      sh = sh.replace(ti + ":", "")
      sh = sh.replace(ti + " :", "")
      sh = sh.replace(ti, "")

  ti = ti.replace("'''''", "").replace("'''", "").replace("''", "")
  # Strange rare edge case where something is bold/italic in the title but not the subheading.

  if (ti in sh):
    if (sh.find(ti) == 0):
      sh = sh.replace(ti + ": ", "")
      sh = sh.replace(ti + ":", "")
      sh = sh.replace(ti + " :", "")
      sh = sh.replace(ti, "")

  datafields["subhead"] = dewhiten(sh)

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
    if "\t" in authors:
      errors += f"\nTab char in authors  : {pagename}"

    authors = dewhiten(authors)

    if authors[:3].lower() == "by ":
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
      authors[i] = dewhiten(authors[i])
      if authors[i] == "":
        authors[i] = "none"
      else:
        # Clean out trailing period.
        if authors[i][-1] in [".", ","]:
          errors += f"\nTrail punct in auths : {pagename}"
          authors[i] = authors[i][:-1]
    return(authors, errors)
  except Exception as err:
    print(f"BIG author error     : {err}")
    errors += f"\nBIG author error     : {pagename}"
    authors = "ERROR"
    return(authors, errors)


def dewhiten(st):
  st = st.replace("\t", " ").replace("\n", " ").strip()
  while "  " in st:
    st = st.replace("  ", " ")
  return st.strip()

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
  datestamp = ""
  datestamp += str(current_year)
  datestamp += "-" + str(current_month).zfill(2)
  datestamp += "-" + str(current_day).zfill(2)
  datestamp += " " + str(current_hour).zfill(2)
  datestamp += ":" + str(current_minute).zfill(2)
  datestamp += ":" + str(current_second).zfill(2)
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

  if ("help" in sys.argv) or ("-h" in sys.argv) or ("--help" in sys.argv):
    print("metadata_fetcher.py")
    print("   ")
    print("   Retrieves and adds metadata, like titles and authors, to")
    print("   Signpost article entries for a given date range.")
    print("   ")
    print("   Uses the article_fetcher module to retrieve a list of")
    print("   all Signpost articles published in the specified date")
    print("   range. This returns a dictionary with basic article info")
    print("   like dates and section names. Then it iterates through")
    print("   every article and makes batched API calls to retrieve the")
    print("   wikitext from the Revisions endpoint (50 per request).")
    print("   Parses the page with mwparserfromhell to extract the")
    print("   article headline, author list, subheadline, et cetera.")
    print("   Cleans up the author string into a list of usernames.")
    print("   Adds the title and author list to each article's entry")
    print("   in a JSON dictionary compatible with Signpost Lua indices")
    print("   and saves it to a JSON file named `<year>-metadata.txt`.")
    print("   ")
    print("   Can be called directly from the command line with format:")
    print("python3 metadata_fetcher.py start[-end] [-html] [-d]")
    print("   All of the following are valid ways to invoke the script:")
    print("python3 metadata_fetcher.py 2017")
    print("python3 metadata_fetcher.py 2011-2020")
    print("python3 metadata_fetcher.py 2005-2005 --debug --html")
    print("   Arguments:")
    print("   ")
    print("startyear, endyear (both optional)")
    print("   Year to fetch metadata for. It can be one year, or a")
    print("   range of years (inclusive) with the start and end")
    print("   point separated by a hyphen. If no year is provided,")
    print("   script defaults to the current year.")
    print("-d, --debug")
    print("   Logs errors (bad characters in metadata fields,")
    print("   unparseable pages, etc) to a file located at")
    print("   data/metadata-errors-YYYY-MM-DD HH:MM:SS.log.")
    print("-html, --html")
    print("   Uses old retrieval method (parses HTML pages with")
    print("   BeautifulSoup instead of wikitext with mwparserfromhell).")
    print("   This doesn't allow advanced metadata retrieval, and")
    print("   doesn't support page batching, so it takes dozens of")
    print("   times longer and produces worse output. Retained as a")
    print("   fallback in case bugs prevent using the default parser.")
    print("-h, --help")
    print("   Prints this help message and exits. ")



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

  mode = "hell"
  debug = False

  if ("-html" in sys.argv) or ("--html" in sys.argv):
    mode = "html"
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
  