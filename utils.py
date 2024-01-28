import orjson


def load_messages():
    with open('./result.json', 'rb') as fin:
        data = fin.read()
        pj = orjson.loads(data)
        messages = pj['messages']
        return messages
