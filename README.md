# Search Experiments

Search experiments with json result file from telegram desktop history exports using [simdjson](https://simdjson.org).

## Goals

- implement a search engine for telegram history export (json)
- index message text in posts and scraped content from links found
- use bot as an interface to show results of the entered query
- control over the fuzzy search algorithm, typo tolerant search
- the ability for bot to search in multiple channels at once
