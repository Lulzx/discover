# Remember Box 2.0

Powered by AI 🚀

## Goals

- [x] implement a search engine for telegram history export (json)
- [x] index message text in posts and scraped links from content found
- [x] use bot as an interface to show results of the entered query
- [x] control over the fuzzy search algorithm, typo tolerant search



## Roadmap

- [x] index everything
- [ ] categorize everything
- [ ] improve recalling
- [ ] encourage reviewing
- [ ] integrate with web
- [ ] find new connections
- [ ] timeline overview
- [ ] track learning


Ultimately, the goal is to make sure all the information you consume (your input) can lead to increased productivity and creativity (your output) instead of festering and getting forgotten in your mind backyard


## Tech Stack

- embedding model - [bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
- telegram library - [pyrogram](https://github.com/pyrogram/pyrogram)
- similarity search - [usearch](https://github.com/unum-cloud/usearch)
- image model - [uform](https://github.com/unum-cloud/uform)
- json serialization - [orjson](https://github.com/ijl/orjson)

## Analysis

![hourly frequency](/results/hourly_freq.png "hourly frequency")
![post frequency](/results/post_freq.png "post frequency")
![sleep duration](/results/7ma-sleep.png "sleep duration")
