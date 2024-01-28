# Remember Box 2.0

Discover engine powered by AI 🚀


## Roadmap

- [x] **Indexing:**
   - [x] Index message text in Telegram history export (JSON).
   - [x] Index scraped links from content found in messages.

- [ ] **Categorization:**
   - [ ] Organize indexed data into relevant categories for better search results.

- [x] **Fuzzy Search and Typo Tolerance:**
   - [x] Implement a customizable fuzzy search algorithm for typo-tolerant search capabilities.

- [x] **Bot Interface:**
   - [x] Develop a Telegram bot as an interface to facilitate user queries.
   - [x] Display search results for entered queries, utilizing the indexed data.

- [x] **Retrival Improvement:**
   - [x] Enhance the recall mechanism to improve the accuracy and relevance of search results.

- [ ] **Encourage Reviewing:**
   - [ ] Implement features to encourage users to review and provide feedback on search results.

- [ ] **Web Integration:**
   - [ ] Integrate the search engine with a web interface for broader accessibility.

- [ ] **Discover New Connections:**
   - [ ] Explore and implement methods to discover new connections within the indexed data.

- [ ] **Timeline Overview:**
   - [ ] Provide a timeline overview feature for users to navigate through historical data more efficiently.

- [ ] **Learning Tracking:**
    - [ ] Incorporate a learning tracking system to monitor and analyze user interactions for continuous improvement.


## Goal

Ultimately, the goal is to make sure all the information you consume (your input) can lead to increased productivity and creativity (your output) instead of festering and getting forgotten in your mind backyard


## Tech Stack

- embedding model - [bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
- telegram library - [pyrogram](https://github.com/pyrogram/pyrogram)
- similarity search - [usearch](https://github.com/unum-cloud/usearch)
- image model - [uform](https://github.com/unum-cloud/uform)
- json serialization - [orjson](https://github.com/ijl/orjson)

## Analysis

![hourly frequency](/images/hourly_freq.png "hourly frequency")
![post frequency](/images/post_freq.png "post frequency")
![sleep duration](/images/7ma-sleep.png "sleep duration")
