<p align="center">
  <img src="https://raw.githubusercontent.com/jp-x-g/wegweiser/main/wegweiser-logo.jpg" alt="Wegweiser logo" width="400" height="400">
</p>

Various scripts to build and maintain Lua indices and article data for the Signpost.

These scripts are made to be modular. The general architecture of the *Signpost*, which Wegweiser's operation is based on, has a few central principles:
* **Article pages are the canonical origin of information.**  
Individual *Signpost* articles store their own metadata (headline, subheading, author names, etc) and are the canonical source of that data. Whatever it says in the article will be reflected on down the line to the database and to pages that draw from that database. If the article name or the author name needs to be changed, it must be done from the article's own page. Articles do not fetch their own metadata from the database; the database fetches it from them.
* **Module indices are the canonical storehouse of information.**  
While the articles are the origin of truth with respect to data, this data is not readily accessible from the articles, and there is additional data (e.g. tags, pageview statistics) that come from other places (e.g. humans using the tagger script, the pageviews API). Hence:  
The *Signpost* module indices are the location, downstream of the data origin, where data is stored in an accessible, machine-readable, validated format.  
Any page that is using this data should be drawing it straight from the indices and parsed dynamically using a module or similar means. Data should not be drawn out of the indices and used to generate other pages (i.e. individual issue pages that redundantly store the date, department name, headline and subhead for each article; individual byline pages that redundantly list an author's stories; etc).  

Perhaps I am rambling here, but I hope this illustrates an idea of how data is meant to flow, and what Wegweiser is meant to do. It consists of a few categories of scripts.
# Table of contents
* [**Workflow scripts**](#Workflow-scripts)  
These are part of the normal operation of Wegweiser, to wit: querying PrefixIndexes, locating article pages, extracting metadata from article pages, querying the pageview API for view counts on the articles, reading from the module indices, integrating its information with what's already there, and saving it to wiki. Workflow scripts do not modify pages other than the module indices.
    * [metadata_fetcher.py](#metadata_fetcher.py)
    * [viewfetcher.py](#viewfetcher.py)
    * [combiner.py](#combiner.py)
    * [uploader.py](#uploader.py)  

* [**Validation scripts**](#Validation-scripts)  
These analyze index data, report errors (including missing data), and compile statistics.
    * [metadata_statisticizer.py](#metadata_statisticizer.py)
    * [validator.py](#validator.py)    

* [**Utility scripts**](#Utility-scripts)  
These are to assist in manual maintenance tasks, like refactoring, updating or modifying articles or metadata. For example, mass alterations can be made to articles' tags, replacing one tag with another across the database (or deleting it altogether). There are also scripts for doing maintenance work, like extracting lists of pages from categories.
    * [mass_tagger.py](#mass_tagger.py)
    * [mass_retagger.py](#mass_retagger.py)    

* [**Internal scripts**](#Internal-scripts)  
These are scripts that are of limited use to the end user, and are called primarily by other scripts in the course of carrying out their favorite tasks. If you're trying to implement or extend Wegweiser, these are useful.
    * [weg_ver.py](#weg_ver.py)
    * [article_fetcher.py](#article_fetcher.py)
    * [cat_fetcher.py](#cat_fetcher.py)
    * [lua_wrangler.py](#lua_wrangler.py)
    * [lua_serializer.py](#lua_serializer.py)
    * [tsv_to_wikitable.py](#tsv_to_wikitable.py)

# Typical workflows
Update indices from 2011: fetch metadata, combine with existing information, upload to the module index year page, and then compute metadata statistics.
`python3 metadata_fetcher.py 2011; python3 combiner.py 2011 -f -k;python3 uploader.py combined/lua-2011.txt Module:Signpost/index/2011;python3 metadata_statisticizer.py`

Update indices with pageviews for 2023: fetch metadata, fetch pageview counts, combine with existing information, and upload to the module index year page.
`python3 metadata_fetcher.py 2023;python3 viewfetcher.py 2023; python3 combiner.py 2023 -f -k;python3 uploader.py combined/lua-2023.txt Module:Signpost/index/2023 Update`

# Workflow scripts
Scripts that are part of the main workflow of the suite.

## metadata_fetcher.py
Retrieves and adds metadata, like titles and authors, to Signpost article entries for a given date range.  
Can be called directly from the command line, with the format:  
`python3 metadata_fetcher.py startyear[-endyear] [-html/--html] [-d/--debug]`  
All of the following are valid ways to invoke the script:  
`python3 metadata_fetcher.py 2017`  
`python3 metadata_fetcher.py 2011-2020`  
`python3 metadata_fetcher.py 2005-2005 --debug --html`  
### Arguments  
`startyear`, `endyear` (both optional)  
Year to fetch metadata for. It can be one year, or a range of years (inclusive) with the start and end point separated by a hyphen. If no year is provided, defaults to the current year.   
`-d`, `--debug`  
Logs errors (bad characters in metadata fields, unparseable pages, etc) to `data/metadata-errors-YYYY-MM-DD HH:MM:SS.log`.  
`-html`, `--html`  
Uses old retrieval method (parses HTML pages with BeautifulSoup instead of wikitext with mwparserfromhell). This doesn't allow advanced metadata retrieval, and doesn't support page batching, so it takes dozens of times longer and produces worse output. Retained as a fallback in case bugs prevent using the default parser.  
`-b=42`, `--batch=42`  
Overrides default batch size for wikitext API requests (50) with custom parameter.  
`-h`, `--help`  
Prints this help message and exits.  
### What it does
* Uses the `article_fetcher` module to retrieve a list of all Signpost articles published in the specified date range. This returns a dictionary with basic article info like dates and subpage names.
* Iterates through every article entry and makes an API call to retrieve the wikitext from the Revisions endpoint. These calls are batched to a default of 50 pages per request, the maximum available from that endpoint (API URLs are also limited to a maximum of 8202 characters, including URL params and full percent-encoded titles of each page being requested).
* Parses the retrieved wikitext with [mwparserfromhell](mwparserfromhell.readthedocs.io/), to extract the article headline, author list, and RSS description (subheading). Cleans up the strings and parses author list into an array.
* Adds the title, author array, and subheadings to each article's entry in the dictionary.
### Output
* Final updated dictionary, containing titles and authors for every article, is saved to a JSON file named `<year>-metadata.txt`.
* Optionally, logs errors to `data/metadata-errors-YYYY-MM-DD HH:MM:SS.log`.    

> [*Back to top*](#Table-of-contents)

## viewfetcher.py
Retrieves daily pageview data for Signpost articles from the Wikimedia REST API.  
### Arguments  
`year`  
The start and end year to fetch views for. If not provided, defaults to the current year.
### What it does
* Use `article_fetcher` module to get a list of all Signpost articles in the specified date range.
* Iterate through every article and construct a URL to query the pageview API (with the `/pageviews/per-article/en.wikipedia/all-access/user/{article-title}` endpoint)
* Parse the API response and extract view counts for the following ranges: 
 7 days (`d007`), 15 days (`d015`), 30 days (`d030`), 60 days (`d060`), 90 days (`d090`), 120 days (`d120`), and 180 days (`d180`)
* Adds the views dictionary to each article's entry.
### Output
Updated article info with views is saved to a JSON file named `<year>-views.txt`.  

> [*Back to top*](#Table-of-contents)

## combiner.py
Combines data from multiple sources into a single JSON index for articles published in the Wikipedia Signpost in a given year. Used like this:  
`python3 combiner.py 2023 -f -k`
### Arguments 
`year` (required): The year to generate the combined index for, passed as an integer.  
`-f` / `--force` (optional): Force update metadata even if fields already exist.  
`-k` / `--keeptitles` (optional): When updating headlines (in indices) from metadata (in articles), keep existing titles if present rather than overwriting.  
### What it does
* Retrieves raw index data for the given year from the Lua indices, using the `lua_wrangler` module. This contains basic metadata like titles, dates, etc.
* Retrieves a full list of Signpost articles for the given year, using the `article_fetcher` module: this uses PrefixIndex, and can catch things that aren't in the indices. Adds anything that was missing.
* Optionally, updates the Lua data with additional metadata (like authors and tags) from a metadata file. This can be forced to overwrite existing data.
* Optionally, integrates page view statistics into the index by matching Lua entries to view data (which you need to have obtained using `viewfetcher.py`) and adding a views field.
### Output
`combined/combine-<year>.json`: The final combined index with all data, as JSON.  
`combined/lua-<year>.txt`: The combined index formatted as a Lua table, for import into Lua environments.  

> [*Back to top*](#Table-of-contents)

## uploader.py 
`python3 uploader.py [source_file] [page_name] [summary]`  
If invoked on its own, this program will `upload()` using the supplied command-line arguments (all strings). 
### Arguments
`source_file`  
Path to a file you want to upload, which will be parsed as plain text.  
`page_name`  
Destination page on the English Wikipedia. Make sure this isn't something stupid!  
`summary` (optional)  
User-defined edit summary. If supplied, this must not contain any spaces.

If no upload arguments are supplied, it will just print this help message and exit.
### What it does
`upload(source_file, page_name, summary)`  
Retrieves `source_file` and uploads it to `page_name`.  
Uses authentication details from `cfg/login.txt`.  
Auth details should be formatted like this:
> DogBot@General_woofing_tasks  
> asdjkflh23kj4lh789ghasdlrth34978  

Default summary is "`Wegweiser V{weg_ver.str()}`" (which it will append to user-defined summaries).
  
`upload_str(source, page_name, summary)`  
Same as `upload()`, but just uses whatever string you pass into it as `source` rather than trying to open a file.
  
> [*Back to top*](#Table-of-contents)

# Validation scripts
## metadata_statisticizer.py
Gathers metadata from Signpost article indices across all years and generates statistics about tag usage and author contributions over time.  
Takes no command line arguments.
* Retrieve Lua index data for every year from 2005 to the current year using `lua_wrangler`.
* Iterate through the index for each year, and count:
 Number of articles tagged with each tag
 Date of most recent usage for each tag
 Number of articles written by each author
 Date of most recent article for each author
* Output the tag and author statistics as two TSV files:
 Authors: `author`, `count`, `most recent date`  
 Tags: `tag`, `count`, `most recent date`  
* Convert the TSV files into wiki tables using the `tsv_to_wikitable` module.
* Upload the tables to Wikipedia in standard locations:
 Authors: `Wikipedia:Wikipedia Signpost/Statistics/Authors/Table`
 Tags: `Wikipedia:Wikipedia Signpost/Statistics/Tags/Table`
* Also write the tables to disk at:
 Authors: `data/statisticized-auth.txt`com
 Tags: `data/statisticized-tags.txt`  

> [*Back to top*](#Table-of-contents)

## validator.py
Parses all Signpost article index data (encompassing all years), validates data for completeness, and compiles a report on missing or incomplete data, which it stores to `data/validate.txt` and uploads to the wiki.  
Takes no command line arguments.  
* Retrieve Lua index data for every year from 2005 to the current year using `lua_wrangler`.
* Iterate through the index for each year, and count how many entries have values present for key metadata fields like `title`, `authors`, `tags`, etc.
* Saves totals for each field to a validation results dictionary containing:  
  Year  
  Number of index entries  
  Count of entries with each metadata field present  
* Also compiles a list of entries missing each field.
* Outputs the validation results as JSON, and formats it into a wikitext table.
* Outputs the list of entries missing data as a series of subheadings with links to individual items.
* Uploads the table and missing entries list, using `uploader`, to `Wikipedia:Wikipedia_Signpost/Technical/Index_validation`.

> [*Back to top*](#Table-of-contents)

# Utility scripts  

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
> [*Back to top*](#Table-of-contents)

## mass_retagger.py
Aliases tags in the indices. Usage is like this:  
`python3 mass_retagger.py badtag goodtag`  
Will apply default aliases (as specified in Module:Signpost/aliases) if invoked with the argument `alias`:  
`python3 mass_retagger.py alias`  
Can also be used to delete tags by providing "delete" as a third argument (second argument will be ignored):  
`python3 mass_retagger.py badtag blahblahblah delete`

> [*Back to top*](#Table-of-contents)

# Internals
Scripts that are called internally; there isn't a whole lot of point in calling them directly but it's possible.
## weg_ver.py
Returns software version (`str()`) and user-agent headers (`headers()`) for the bot.  

> [*Back to top*](#Table-of-contents)

## article_fetcher.py
Queries the Wikipedia API to retrieve a list of all Signpost articles published within a given date range and return it as a dict or an array. It has one main callable function:
> `fetch(year_start, year_end, month_range=13, format="dict")`
### Arguments
`year_start` (int)  
Earliest year to include
`year_end` (int)  
Most recent year to include
`month_range` (int)  
Number of months to query per year (defaults to full year)
`format` (str)  
Output format, either "`dict`" or "`array`"
### What it does
* Constructs a series of API query URLs to fetch article titles from the specified date range, month-by-month. Requests data from the `allpages` module.  
 * Technically, this is limited -- to five hundred articles in one month. This is very unlikely to ever matter; even if the Signpost published every single day and had ten articles per issue, there would be no more than 310 articles in a month. But it is worth noting that if, in the future, something really bizarre happens, the limit may need to be increased.*
* Calls each API URL and extracts the returned list of article titles.  
* Parses each page name to extract the issue date and article department. This does *not* involve retrieving or parsing the actual text of the page.
### Output
Returns the article data in one of two formats:
* `format="dict"`: A nested dictionary with year > issue date > article metadata
* `format="array"`: A simple ordered list of article titles.  

> [*Back to top*](#Table-of-contents)

## cat_fetcher.py
Utility for getting lists of pages in Wikipedia categories.  Has one function.  

`fetch(cat)`  
Retrieves members of Category:`cat`, and returns it as an array of page names. Limited to 500.  
Optional parameter `complete=True` will return an array of three-item dicts, with keys `pageid`, `ns` and `title`.   

`main` (not called from any other script; executes if you run cat_fetcher.py from the command line)  
Prints this message, `fetch`es whatever `cat` you give as an arg, and exits.  
> [*Back to top*](#Table-of-contents)

## lua_wrangler.py
Retrieves Lua tables from web and converts them into Python.

`fetch(year)`  
Retrieves wikitext of Module:Signpost/index/year,  converts Lua table to a Python object, and returns it.

`luaify(obj)`  
Serializes a Python object to a Lua table.  

`main` (not called from any other script; executes if you run lua_wrangler.py from the command line)  
Print this message, retrieve and print index for the current year, and (optionally) save it to an output file, e.g. "`python3 lua_wrangler.py output.txt`" or whatever. 
> [*Back to top*](#Table-of-contents)

## lua_serializer.py
Serializes a Python object to a Lua table.  
### Arguments  
`obj` (number, int, float, str, dict, list)  
The object to serialize.

`indent` (str, optional)  
The string to indent with, e.g. `\t` or `  `.

`indent_level` (int, optional)  
The initial indentation level.

`min_single_line_indent_level` (int, optional)  
At this indentation level or above, tables will be formatted on a single line.

`table_sort_key` (Callable, optional)  
A key function with which to sort keys of Lua tables. If not specified, the table is not sorted. For details of key functions, see https://docs.python.org/3/howto/sorting.html#key-functions.
### Output  
`string`  
Returns a serialized Lua data table string.  
> [*Back to top*](#Table-of-contents)

## tsv_to_wikitable.py
Converts TSVs to formatted tables in wikitext markup.

`process(data, headers)`  
Omits file processing, and simply parses `data` (a string) into a wikitable (using the optional `headers` array, if present, for column headings). Returns a string of the formatted wikitable.  

`convert(input_file, output_file, headers)`  
Converts `input_file` (default `input.txt`) to wikitable, using `process()`, with optional `headers` array for column headings. Writes result to `output_file` (default `output.txt`).

`main` (not called from any other script; executes if you run lua_wrangler.py from the command line)  
Invoked like this: `python3 tsv_to_wikitable.py uglytext.txt nicetable.txt`  
Supplying one argument (just the input file) will write, by default, to `output.txt`.  
Supplying no arguments will parse `input.txt` and write to `output.txt`.