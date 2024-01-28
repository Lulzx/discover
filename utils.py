import orjson
from timeit import default_timer as timer


def load_messages():
    with open('./result.json', 'rb') as fin:
        data = fin.read()
        pj = orjson.loads(data)
        messages = pj['messages']
        return messages


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


def time_elapsed(start_time):
    return f'{(timer() - start_time) * 1000:.2f}'
