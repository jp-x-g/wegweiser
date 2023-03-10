# JPxG 2023 01 07
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
import weg_ver


def purge(page_name, summary=f"Null edit - Wegweiser V{weg_ver.str()}"):

	s = requests.Session()
	
	api_base = "https://en.wikipedia.org/w/api.php"
	auth_path = "cfg/login.txt"

	print(f"Attempting to purge {page_name}.")

	raw_url = "https://en.wikipedia.org/w/index.php?title=" + urllib.parse.quote(page_name, safe='') + "&action=raw"

	source = s.get(raw_url).text

	# print(source)

	f = open(auth_path, "r")
	auth = f.read()
	f.close()
	auth = auth.split("\n")

	print(auth)
	
	print(f"Attempting to authenticate.")
	print(f"Username: {auth[0]}")
	print(f"Password: {auth[1][0] + '0'.zfill(len(auth[1]) - 1).replace('0', '*')}")
	
	token_url = api_base + "?action=query&meta=tokens&format=json&type=login"
	edit_token_url = api_base + "?action=query&meta=tokens&format=json"
	# The token and login attempt must be part of the same session, or else it'll time out.

	t = s.get(token_url)
	########## This line actually hits the API.
	token = json.loads(t.text)["query"]["tokens"]["logintoken"]
	# Stores the result as "token"
	print("Token retrieved. Attempting login.")
	l = ""
	l = s.post(
		api_base,
		data={
			"action": "login",
			"lgname": auth[0],
			"lgpassword": auth[1],
			"lgtoken": token,
			"format": "json",
			},
		)
	if l.status_code != 200:
		print(f"Received status code from login request: {l.status_code}")
		quit()
	########## This line actually hits the API.
	print(l)
	l = json.loads(l.text)
	if (l["login"]["result"]) != "Success":
		print("!!! Login failed: " + str(l))
		quit()
	print("Login successful. Authenticated as " + l["login"]["lgusername"])
	print(l)

	########## Now we are logged in, and free to roam.

	t = s.get(edit_token_url)
	########## This line actually hits the API for an edit token.
	token = json.loads(t.text)["query"]["tokens"]["csrftoken"]

	########## Okay, let's actually send the darn thing.
	edit = s.post(
		api_base,
		data={
			"action": "edit",
			"token": token,
			"title": page_name,
			"text": source,
			"summary": f"{summary} / Trial run from [[Wikipedia:Bots/Requests for approval/WegweiserBot|BRFA]] (Wegweiser V{weg_ver.str()})",
			"format": "json",
		},
	)
	edit = edit.text
	# print(edit)
	edit = json.loads(edit)
	print(edit)


def purge_list(list_file):
		f = open(str(list_file), "r")
		pages = f.read()
		f.close()
		pages = pages.split("\n")
		print(f"Loaded {len(pages)} pages.")
		counter = 0
		for page in pages:
			print(f"Completed {str(counter).zfill(5)} of {str(len(pages)).zfill(5)}")
			purge(page)
			counter += 1
		print("Complete.")


if (__name__ == "__main__"):

	if len(sys.argv) == 2:
		purge_list(str(sys.argv[1]))
	else:
		print("/!\\ This file is usually not run on its own!")
		print("uploader.py:")
		print("> purge(page_name)")
		print("  Performs a null-edit to purge the cache of that page.")
		print("  Uses authentication details from cfg/login.txt")
		print("  Auth details should be formatted like this:")
		print("  ")
		print("DogBot@General_woofing_tasks")
		print("asdjkflh23kj4lh789ghasdlrth34978")
		print("  ")
		print("> purge_list(list_file)")
		print("  Performs purge() on a list of titles,")
		print("  loaded from list_file (separated by line breaks).")
		print("  ")
		print("> If invoked by its own, this program will load page names")
		print("  from whatever location you specify as an argument:")
		print("python3 purger.py [source_file]")
		print("  If no upload arguments are supplied, it will just exit.")
		print("  ")
		exit()