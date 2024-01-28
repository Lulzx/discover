import time
from utils import load_messages

start = time.time()

links = set()

messages = load_messages()

for message in messages:
    text_entities = message.get('text_entities', [])
    for entity in text_entities:
        if entity.get('type') == 'link':
            url = entity.get('text')
            links.add(url)


with open("links.txt", "wb", buffering=8192) as f:
    for link in links:
        f.write(f"{link}\n".encode("utf8"))

end = time.time()

print(end-start)
