import os
from timeit import default_timer
import orjson
import numpy as np
from tqdm import tqdm
from typing import List
from fastembed.embedding import DefaultEmbedding
from utils import load_messages
from concurrent.futures import ProcessPoolExecutor


def end_timer(start_time):
    return (default_timer() - start_time) * 1000

def extract_text(element):
    if isinstance(element, list):
        return ''.join(map(extract_text, element))
    elif isinstance(element, dict) and "text" in element:
        return extract_text(element["text"])
    elif isinstance(element, str):
        return element
    else:
        return ""

embedding_model = DefaultEmbedding()

messages = load_messages()
messages = messages[:10]

message_dicts = [{'id': message['id'], 'text': extract_text(message)} for message in messages]
message_texts = [message['text'] for message in message_dicts]

documents: List[str] = message_texts

if os.path.exists('raw_embeddings.npy'):
    embeddings = np.load('raw_embeddings.npy')
    count = len(embeddings)
    print(f"Loaded {count} embeddings.")
else:
    start_time = default_timer()

    embeddings = list(embedding_model.passage_embed(documents))
    np.save('raw_embeddings.npy', embeddings)

    time_elapsed = end_timer(start_time)
    count = len(embeddings)
    print(f"{count} embeddings generated in {time_elapsed:.2f} ms")

for i, message_dict in enumerate(message_dicts):
    message_dict['embedding'] = embeddings[i].tolist()

try:
    with open('messages.json', 'w') as json_file:
        json_file.write(orjson.dumps(message_dicts, option=orjson.OPT_INDENT_2).decode('utf-8'))
    print("Saved message texts with embeddings!")
except Exception as e:
    print(f"An error occurred: {e}")

start_time = default_timer()

query = input("query: ")
query_embedding = next(embedding_model.query_embed(query))

def print_top_k(query_embedding, embeddings, documents, k=min(5, count)):
    scores = np.dot(embeddings, query_embedding)
    sorted_indices = np.argsort(scores)[::-1][:k]
    for i, idx in enumerate(sorted_indices):
        print(f"Rank {i+1}: Score={scores[idx]:.4f}, Document: {documents[idx]}")

print(f"Searching for: {query}")
print_top_k(query_embedding, embeddings, documents)

time_elapsed = end_timer(start_time)
print(f"Search took {time_elapsed:.2f} ms")
