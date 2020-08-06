import time

with open("./result.json", 'rb') as f:
    data = f.read()

start = time.time()
data = data.lower()
end = time.time()

with open('./lower.json', 'wb') as foo:
    foo.write(data)

print(end - start)