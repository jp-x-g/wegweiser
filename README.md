# wegweiser

Various scripts to build and maintain Lua indices for Signpost data.

These scripts are made to be modular. The general architecture of the *Signpost*, which Wegweiser's operation is based on, has a few central principles:
* **Article pages are the canonical origin of information.**  
Individual *Signpost* articles store their own metadata (headline, subheading, author names, etc) and are the canonical source of that data. Whatever it says in the article will be reflected on down the line to the database and to pages that draw from that database. If the article name or the author name needs to be changed, it must be done from the article's own page. Articles do not fetch their own metadata from the database; the database fetches it from them.
* **Module indices are the canonical storehouse of information.**  
While the articles are the origin of truth with respect to data, this data is not readily accessible from the articles, and there is additional data (e.g. tags, pageview statistics) that come from other places (e.g. humans using the tagger script, the pageviews API). Hence:  
The *Signpost* module indices are the location, downstream of the data origin, where data is stored in an accessible, machine-readable, validated format.  
Any page that is using this data should be drawing it straight from the indices and parsed dynamically using a module or similar means. Data should not be drawn out of the indices and used to generate other pages (i.e. individual issue pages that redundantly store the date, department name, headline and subhead for each article; individual byline pages that redundantly list an author's stories; etc).  

Perhaps I am rambling here, but I hope this illustrates an idea of how data is meant to flow, and what Wegweiser is meant to do. It consists of a few categories of scripts:
* **Workflow scripts**  
These are part of the normal operation of Wegweiser, to wit: querying PrefixIndexes, locating article pages, extracting metadata from article pages, querying the pageview API for view counts on the articles, reading from the module indices, integrating its information with what's already there, and saving it to wiki. Workflow scripts do not modify pages other than the module indices.

* **Utility scripts**  
These are to assist in manual maintenance tasks, like refactoring, updating or modifying articles or metadata. For example, mass alterations can be made to articles' tags, replacing one tag with another across the database (or deleting it altogether). There are also scripts for doing maintenance work, like extracting lists of pages from categories.

* **Internal scripts**  
These are scripts that are of limited use to the end user, and are called primarily by other scripts in the course of carrying out their favorite tasks. If you're trying to implement or extend Wegweiser, these are useful.

# Typical workflows
Update indices from 2011: fetch metadata, combine with existing information, upload to the module index year page, and then compute metadata statistics.
`python3 metadata_fetcher.py 2011; python3 combiner.py 2011 -f -k;python3 uploader.py combined/lua-2011.txt Module:Signpost/index/2011;python3 metadata_statisticizer.py`

Update indices with pageviews for 2023: fetch metadata, fetch pageview counts, combine with existing information, and upload to the module index year page.
`python3 metadata_fetcher.py 2023;python3 viewfetcher.py 2023; python3 combiner.py 2023 -f -k;python3 uploader.py combined/lua-2023.txt Module:Signpost/index/2023 Update`

# Individual workflow scripts
Scripts that are part of the main workflow of the suite: 

## article_fetcher.py
## json-tabler.py
## main.py
## mass_tagger.py

This script is for mass-tagging of articles whose subpages match a mask.
That is to say, if you want to tag all "Arbitration report" articles with
"arbitrationreport", or whatever.  
It can also fetch from categories, i.e. extract all pages from a certain category
and then add them to whatever tag you give as an argument.
Like this:  
`python3 mass_tagger.py 2005 Wikipedia_Signpost_Year_in_review yearinreview`

It can also just add a tag to every article that's in a certain list.
This is done by specifying the fourth parameter.
Like this:
`> python3 mass_tagger.py 2005 nocat acejan2006 mass_tag.txt`

## purger.py
## tsv_to_wikitable.py

## lua_serializer.py
Serializes a Python object to a Lua table.  
**Arguments:**  
`obj` (number, int, float, str, dict, list)  
The object to serialize.  
`indent` (str, optional)  
The string to indent with, e.g. "\t" or "  ".  
`indent_level` (int, optional)  
The initial indentation level.  
`min_single_line_indent_level` (int, optional)  
At this indentation level or above, tables will be formatted on a single line.  
`table_sort_key` (Callable, optional) 
A key function with which to sort keys of Lua tables. If not specified, the table is not sorted. For details of key functions, see https://docs.python.org/3/howto/sorting.html#key-functions.

**Returns:**  
`string`  
A serialized Lua data table string.

## uploader.py
> Has two functions.

`upload(source_file, page_name, summary)`

  Retrieves source_file and uploads it to page_name.
  
  Uses authentication details from cfg/login.txt
  
  Auth details should be formatted like this:
> DogBot@General_woofing_tasks

> asdjkflh23kj4lh789ghasdlrth34978

  Default summary is `Wegweiser V{weg_ver.str()}`.
  
`upload_str(source, page_name, summary)`

  Same as upload(), but just uses whatever string you pass into it as 'source'.

If invoked by its own, this program will upload whatever is passed to it using this format:

`python3 uploader.py [source_file] [page_name]`

If no upload arguments are supplied, it will just print this message and exit.


## mass_tagger_list.py

## metadata_fetcher.py
Retrieves and adds metadata, like titles and authors, to Signpost article entries for a given date range.

Arguments:
> year (optional): The start and end year to fetch metadata for. If not provided, defaults to the current year.

What it does:
- Uses the `article_fetcher` module to retrieve a list of all Signpost articles published in the specified date range. This returns a dictionary with basica article info like dates and section names.
- Iterates through every article entry and makes an API call to retrieve the Wikipedia page HTML.
- Parses the page with BeautifulSoup to extract the article headline and author list. Cleans up the author string into a list of usernames.
- Adds the title and author list to each article's entry in the dictionary.
- Saves the final updated dictionary containing titles and authors for every article to a JSON file named <year>-metadata.txt.
## viewfetcher.py
## combiner.py
Combines data from multiple sources into a single JSON index for articles published in the Wikipedia Signpost in a given year. Used like this:
>  python3 combiner.py 2023 -f -k

Arguments:
> year (required): The year to generate the combined index for, passed as an integer.
> -f/--force (optional): Force update metadata even if fields already exist.
> -k/--keeptitles (optional): When updating titles from metadata, keep existing titles if present rather than overwriting.

What it does:
- Retrieves raw index data for the given year from the Lua indices, using the `lua_wrangler` module. This contains basic metadata like titles, dates, etc.
- Retrieves a full list of Signpost articles for the given year, using the `article_fetcher` module: this uses PrefixIndex, and can catch things that aren't in the indices. Adds anything that was missing.
- Optionally, updates the Lua data with additional metadata (like authors and tags) from a metadata file. This can be forced to overwrite existing data.
- Optionally, integrates page view statistics into the index by matching Lua entries to view data (which you need to have obtained using `viewfetcher.py`) and adding a views field.

Finally, it outputs two files:

> combined/combine-<year>.json: The final combined JSON index with all data.
> combined/lua-<year>.txt: The combined index formatted as a Lua table, for import into Lua environments.


## metadata_statisticizer.py

## validator.py


# Utility scripts

## mass_retagger.py
Aliases tags in the indices. Usage is like this:  
`python3 mass_retagger.py badtag goodtag`  
Will apply default aliases (as specified in Module:Signpost/aliases) if invoked with the argument `alias`:  
`python3 mass_retagger.py alias`  
Can also be used to delete tags by providing "delete" as a third argument:  
`python3 mass_retagger.py badtag blahblahblah delete`


# Internals
Scripts that are called internally; there is typically not a reason to invoke these from the terminal, but if you want to, you can.
## weg_ver.py
Stores software version and user-agent headers for the bot. 
## cat_fetcher.py
> This file is usually not run on its own!

cat_fetcher:
> fetch(cat): retrieves members of Category:Whatever,
  and returns it as an array of page names.
  Limited to 500."
  Optional parameter 'complete=True' will return
  an array of three-item dicts, with keys
  'pageid', 'ns' and 'title'.
> main (not called from any other script):")
  Prints this message,
  fetches whatever cat you give as an arg,
  and exits.
## lua_wrangler.py
> This file is usually not run on its own!

lua_wrangler.py has several functions:
> fetch(year): retrieves wikitext of Module:Signpost/index/year,
  converts Lua table to a Python object, and returns it.
> luaify(obj): serializes a Python object to a Lua table.
> main (not called from any other script):
  print this message, retrieve and print index for CURRENTYEAR,
  and (optionally) save it to an output file, viz.
  "python3 lua_wrangler.py output.txt" or whatevre.
