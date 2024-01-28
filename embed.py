from timeit import default_timer
import orjson
import numpy as np
from tqdm import tqdm
from typing import List
from fastembed.embedding import DefaultEmbedding
from utils import load_messages
from concurrent.futures import ProcessPoolExecutor

def start_timer():
    start_time = default_timer()

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

start_time = default_timer()

messages = load_messages()

message_dicts = [{ 'id': message['id'], 'text': extract_text(message) } for message in messages]

message_texts = [message['text'] for message in message_dicts]

start_timer()

documents: List[str] = message_texts
embedding_model = DefaultEmbedding()

embeddings: List[np.ndarray] = []
total_docs = len(documents)

progress_bar = tqdm(total=total_docs, desc="Generating Embeddings", unit="doc")

for document in documents:
    embeddings.extend(embedding_model.passage_embed([document]))
    progress_bar.update(1)

progress_bar.close()

time_elapsed = end_timer(start_time)

count = len(embeddings)
print(f"{count} embeddings generated in {time_elapsed:.2f} ms")

try:
    with open('raw_embeddings.txt', 'w') as embedding_file:
        embedding_file.write(str(embeddings))
    print("embeddings saved successfully!")
except Exception as e:
    print(f"an error occured: {e}")


for i, message_dict in enumerate(message_dicts):
    message_dict['embedding'] = embeddings[i].tolist()

try:
    with open('messages.json', 'w') as json_file:
        json_file.write(orjson.dumps(message_dicts, option=orjson.OPT_INDENT_2).decode('utf-8'))
    print("saved message texts with embeddings!")
except Exception as e:
    print(f"an error occured: {e}")


start_timer()

query = "Who maintains fastembed?"
query_embedding = list(embedding_model.query_embed(query))[0]

def print_top_k(query_embedding, embeddings, documents, k=min(5, count)):
    scores = np.dot(embeddings, query_embedding)
    sorted_scores = np.argsort(scores)[::-1]
    for i in range(k):
        print(f"Rank {i+1}: {documents[sorted_scores[i]]}")

print(f"searching for: {query}")
print_top_k(query_embedding, embeddings, documents)

time_elapsed = end_timer(start_time)
print(f"search took {time_elapsed:.2f} ms")
