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


def upload(source_file, page_name, summary=f"Wegweiser V{weg_ver.str()}"):
	"""
	Upload from a file.
	"""

	f = open(str(source_file), "r")
	source = f.read()
	f.close()
	print(f"Loaded source file: {source_file}")
	print(f"Size: {sys.getsizeof(source)}")

	upload_str(source, page_name, summary)

def upload_str(source, page_name, summary=f"Wegweiser V{weg_ver.str()}"):
	"""
	Upload any string from Python.
	"""
	print(f"Attempting to upload to {page_name}")

	api_base = "https://en.wikipedia.org/w/api.php"
	auth_path = "cfg/login.txt"

	f = open(auth_path, "r")
	auth = f.read()
	f.close()
	auth = auth.split("\n")
	
	#print(f"Attempting to authenticate.")
	print(f"Authenticating. User: {auth[0]}, password: {auth[1][0] + '0'.zfill(len(auth[1]) - 1).replace('0', '*')}")
	
	token_url = api_base + "?action=query&meta=tokens&format=json&type=login"
	edit_token_url = api_base + "?action=query&meta=tokens&format=json"
	# The token and login attempt must be part of the same session, or else it'll time out.

	s = requests.Session()

	t = s.get(token_url)
	########## This line actually hits the API.
	token = json.loads(t.text)["query"]["tokens"]["logintoken"]
	# Stores the result as "token"
	#print("Token retrieved. Attempting login.")
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
	#print(l)
	l = json.loads(l.text)
	if (l["login"]["result"]) != "Success":
		print("!!! Login failed: " + str(l))
		quit()
	#print("Login successful. Authenticated as " + l["login"]["lgusername"])
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
			"summary": f"{summary} / (Wegweiser V{weg_ver.str()})",
			"format": "json",
		},
	)
	edit = edit.text
	# print(edit)
	edit = json.loads(edit)
	print(edit)


if (__name__ == "__main__"):

  if len(sys.argv) == 4:
  	upload(str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]))
  elif len(sys.argv) == 3:
  	upload(str(sys.argv[1]), str(sys.argv[2]))
  else:
  	print("uploader.py:")
  	print("> Has two functions.")
  	print("> upload(source_file, page_name, summary)")
  	print("  Retrieves source_file and uploads it to page_name.")
  	print("  Uses authentication details from cfg/login.txt")
  	print("  Auth details should be formatted like this:")
  	print("DogBot@General_woofing_tasks")
  	print("asdjkflh23kj4lh789ghasdlrth34978")
  	print(f"  Default summary is 'Wegweiser V{weg_ver.str()}'")
  	print("  ")
  	print("> upload_str(source, page_name, summary)")
  	print("  Same as upload(), but just uses whatever string")
  	print("  you pass into it as 'source'.")
  	print("  ")
  	print("> If invoked by its own, this program will upload")
  	print("  whatever is passed to it using this format:")
  	print("python3 uploader.py [source_file] [page_name]")
  	print("  If no upload arguments are supplied, it")
  	print("  will just print this message and exit.")
  	print("  ")
  	exit()