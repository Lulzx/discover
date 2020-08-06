import time
import simdjson

parser = simdjson.Parser()

start = time.time()
with open('./result.json', 'rb') as fin:
    pj = parser.parse(fin.read())
    print(pj.at('name'))
    messages = pj['messages'].as_list()
    print(pj.keys())

t = input("Enter search query: ").lower()
indices = []
for i in range(len(messages)):
	text = str(messages[i]['text'])
	if t in text:
		indices.extend([messages[i]['id']])
print("post id(s): ", indices)

end = time.time()

time_elapsed = end - start
print(len(indices), "item(s) found in", str(time_elapsed)[:5] + ' ms')
