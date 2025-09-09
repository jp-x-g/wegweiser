def str():
	return "2.0"

def summary():
	return f"Wegweiser/{str()} (https://en.wikipedia.org/wiki/User:WegweiserBot)"

def headers():
	return {"User-Agent": f"{summary()}"}

# The only function of this script is to return the version string and/or user-agent headers.
# 2.0, 2023-12-15