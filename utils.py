import orjson
from timeit import default_timer as timer


def load_messages():
    with open('./result.json', 'rb') as fin:
        data = fin.read()
        pj = orjson.loads(data)
        messages = pj['messages']
        return messages


def time_elapsed(start_time):
    return f'{(timer() - start_time) * 1000:.2f}'


def extract_text(element) -> str:
    if isinstance(element, list):
        return ''.join(map(extract_text, element))
    elif isinstance(element, dict) and "text" in element:
        return extract_text(element["text"])
    elif isinstance(element, str):
        return element
    else:
        return ""


def get_messages():
    messages = load_messages()
    extracted_messages = [{'id': message['id'], 'text': extract_text(message)} for message in messages]
    return [extract_text(message) for message in extracted_messages]


def list_builder(indices):
    string = ""
    len_indices = len(indices)
    if len_indices > 1:
        for n, x in enumerate(indices):
            y = "[{}](https://t.me/c/1083858375/{})".format(x,x)
            if n < len_indices - 1:
                string += "├ " + y + "\n"
            else:
                string += "└ " + y
    else:
        string += "└ " + str(indices[0])
    return string
