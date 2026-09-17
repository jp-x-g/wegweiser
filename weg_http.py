# Claude 2026 09 16
"""
One shared, polite, retrying HTTP session for all the Wegweiser scripts.

Why this exists: every fetcher used to call requests.get() directly, in a
tight loop, with no delay and no retries. Sooner or later Wikimedia decides
we are hammering it, starts returning HTTP 429 with an HTML error page
instead of JSON, and the fetchers -- which only checked for status 200 --
would return an error *string* where the caller expected a list of articles.
Downstream code then iterated that string one character at a time and died
with "TypeError: string indices must be integers", in a different script,
a thousand lines of output later, pointing at a year that had nothing to do
with anything. Great fun.

So, now:
  - one Session, so connections (and cookies) get reused
  - automatic backoff on 429 and 5xx, honoring the Retry-After header
  - a minimum interval between requests, so we don't earn the 429 to start
  - and if it STILL fails, a FetchError that says what actually happened,
    at the point where it actually happened.

Knobs, if you need them:
  WEG_DELAY    seconds between requests (default 0.1)
  WEG_RETRIES  how many times to retry a 429/5xx (default 5)
"""
import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import weg_ver

# These are the ones worth trying again: rate limits and server hiccups.
# A 404 is a real answer to the question, so it is not in here.
RETRY_STATUSES = (429, 500, 502, 503, 504)

MIN_INTERVAL = float(os.environ.get("WEG_DELAY", "0.1"))
MAX_RETRIES  = int(os.environ.get("WEG_RETRIES", "5"))


class FetchError(Exception):
  """The API didn't give us anything we can actually use."""


def new_session():
  """
  A fresh session with the retry policy attached. Use this if you need your
  own cookie jar (the uploader does, for login), otherwise just use the
  shared 'session' below.
  """
  s = requests.Session()
  s.headers.update(weg_ver.headers())
  retry = Retry(
    total=MAX_RETRIES,
    backoff_factor=1.5,
    # 1.5s, 3s, 6s, 12s, 24s -- unless Retry-After says otherwise, which it
    # usually does, and which we obey.
    status_forcelist=RETRY_STATUSES,
    allowed_methods=frozenset(["GET", "POST"]),
    respect_retry_after_header=True,
    raise_on_status=False,
    # We'd rather hand the response back and raise our own error with a
    # readable message than let urllib3 throw MaxRetryError at us.
  )
  adapter = HTTPAdapter(max_retries=retry)
  s.mount("https://", adapter)
  s.mount("http://", adapter)
  return s


session = new_session()

_last_request = 0.0


def _throttle():
  # Space requests out a bit. Cheap insurance: the backoff above only helps
  # once we're already in trouble.
  global _last_request
  wait = MIN_INTERVAL - (time.monotonic() - _last_request)
  if wait > 0:
    time.sleep(wait)
  _last_request = time.monotonic()


def explain(response, url):
  """Turn a sad response into a sentence a human can act on."""
  if response.status_code == 429:
    return (
      f"HTTP 429 (rate limited) retrieving {url}\n"
      f"    Wikimedia is throttling us, and {MAX_RETRIES} retries with backoff "
      f"weren't enough.\n"
      f"    Wait a while and run it again, or slow the whole thing down with "
      f"WEG_DELAY (currently {MIN_INTERVAL}s between requests)."
    )
  return f"HTTP {response.status_code} retrieving {url}"


def get(url, tolerate=(), sess=None):
  """
  GET a URL. Returns the response on 200.

  Anything in 'tolerate' (say, a 404 for an article with no pageviews yet)
  comes back as None, so the caller can shrug and move on. Anything else
  raises FetchError, loudly, right here.
  """
  _throttle()
  response = (sess or session).get(url)
  if response.status_code == 200:
    return response
  if response.status_code in tolerate:
    return None
  raise FetchError(explain(response, url))


def parse_json(response, url):
  """
  response.json(), but if the body isn't JSON it says so instead of throwing
  a JSONDecodeError about line 1 column 1. Usually that body is an HTML
  error page from Varnish, which is worth quoting back at you.
  """
  try:
    return response.json()
  except ValueError:
    body = " ".join(response.text.split())[:300]
    raise FetchError(
      f"Expected JSON from {url}, got {response.headers.get('content-type', 'something else')}.\n"
      f"    First 300 characters: {body}"
    )


def get_json(url, tolerate=(), sess=None):
  """The one everybody actually wants. None if the status was tolerated."""
  response = get(url, tolerate=tolerate, sess=sess)
  if response is None:
    return None
  return parse_json(response, url)


if (__name__ == "__main__"):
  print("/!\\ This file is not run on its own!")
  print("weg_http.py provides:")
  print("> session:        a shared requests.Session with retries and a UA")
  print("> new_session():  your own copy of same")
  print("> get(url):       GET, raising FetchError on anything unusable")
  print("> get_json(url):  same, already deserialized")
  print(f"Currently: {MIN_INTERVAL}s between requests, {MAX_RETRIES} retries on {RETRY_STATUSES}.")
