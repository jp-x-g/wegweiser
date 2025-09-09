# JPxG 2023 01 04
import datetime
import requests
import json
import urllib
import luadata
import sys
import weg_ver
from datetime import datetime
# python -m pip install --upgrade luadata

# This is a secret tool that will come in handy later.
signpost = "Wikipedia Signpost"

def fetch(year_start=2005, year_end=2001, format="dict"):
  headers = weg_ver.headers()
  pref = "Wikipedia:" + signpost + "/Archives/"

  if (year_end == 2001):
    year_end = int(datetime.now().strftime("%Y"))
  # Make "2001" into current year

  issue_list_array = []
  # All of the queries to send to the server and get a PrefixIndex-like list. Not returned.
  issues_array = []
  # Simple array of the issues, one by one.
  all_issues = {}
  # Formatted dict of all the issues.
  all_issues_mod = {}
  # Formatted dict of all the issues, in the style of the module.
  for year in range(year_start, (year_end + 1)):
    all_issues[str(year)] = {}
    all_issues_mod[str(year)] = []
    for month in range(1,13):
      mo = str(month)
      if month < 10:
        mo = "0" + mo
      all_issues[str(year)][mo] = []

  #print(all_issues)

  for year in range(year_start, (year_end + 1)):
    issue_list_query = f"https://en.wikipedia.org/w/api.php?format=json&action=query&list=allpages&apprefix={signpost}%2FArchives/{year}-&aplimit=max&apnamespace=4"
    # Dash is necessary: we need to, e.g. prefix with "2005-" instead of "2005"
    # so our index excludes the year pages like "Wikipedia:Wikipedia_Signpost/Archives/2005"
    issue_list_array.append(issue_list_query)

  # Now we hit the API to populate the articles_array.
  for url in issue_list_array:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      print(f'Retrieved {url}')
      data = response.json()
      for item in data["query"]["allpages"]:
        # print(item["title"])
        issues_array.append(item["title"].replace(pref, ""))
    else:
      print(f'Error retrieving {url}')

  #print(articles_array)

  issues_array.sort()

  # Now we will make a dict, for the optional method that returns one.
  # This will have each issue as, e.g. issues[2022][08].

  for issue in issues_array:
    # We got the titles, but trimmed them:
    # Wikipedia:Wikipedia_Signpost/Archives/2022-08-01
    # |                                     |
    # 000000000011111111112222222222333333333344444444445
    # 012345678901234567890123456789012345678901234567890
    # |    |  |
    # 2022-08-01

    issue_y = issue[:4]
    issue_m = issue[5:7]
    issue_d = issue[8:]
    # print(f"{issue_y} / {issue_m} / {issue_d} / {article_dept}")
    all_issues[str(issue_y)][str(issue_m)].append(issue)
    all_issues_mod[str(issue_y)].append(issue)

  if format == "dict":
    return all_issues
  if format == "dict_mod":
    return all_issues_mod
  if format == "array":
    return issues_array
  return "Error: invalid output format specified for issue fetcher."

if (__name__ == "__main__"):
  all_issues = fetch(format="dict")
  print(all_issues)
  all_issues = fetch(format="dict_mod")
  print(all_issues)
  all_issues = fetch(format="array")
  print(all_issues)