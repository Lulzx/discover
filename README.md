# Search Experiments

Search experiments with json result file from telegram desktop history exports using [orjson](https://pypi.org/project/orjson/).

## Goals

- [x] implement a search engine for telegram history export (json)
- [x] index message text in posts and scraped links from content found
- [x] use bot as an interface to show results of the entered query
- [ ] control over the fuzzy search algorithm, typo tolerant search
- [ ] the ability for bot to search in multiple channels at once

![post frequency](/results/post_freq.png "post frequency")

# Remember Box 2.0

Powered by AI 🚀

## Roadmap
- index everything
- categorize everything
- improve recalling
- encourage reviewing
- integrate with web
- find new connections
- timeline overview
- track learning

![hourly frequency](/results/hourly_freq.png "hourly frequency")

Ultimately, the goal is to make sure all the information you consume (your input) can lead to increased productivity and creativity (your output) instead of festering and getting forgotten in your mind backyard

## Tech Stack
- embedding model - bge-small-en-v1.5
- telegram library - pyrogram
- similarity search - usearch
- image model - uform

![sleep duration](/results/7ma-sleep.png "sleep duration")
