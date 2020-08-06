import json
import time
from urlextract import URLExtract

start = time.time()

extractor = URLExtract()

with open('result.json', encoding="utf8") as f:
  data = json.load(f)

posts = json.dumps(data)

links = []

for url in extractor.gen_urls(posts):
    links.append(url)

with open("links.txt", "w") as f:
    for link in links:
        f.write(str(link) +"\n")

end = time.time()

print(end-start)