import os
import orjson
from utils import get_messages
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def categorize_messages(n_clusters: int = 5, output_path: str = 'cache/categories.json') -> None:
    """Cluster messages into categories using TF-IDF and KMeans."""
    messages = get_messages()
    if not messages:
        print('No messages found for categorization')
        return

    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(messages)

    km = KMeans(n_clusters=n_clusters, random_state=42)
    labels = km.fit_predict(X)

    categorized = []
    for msg, label in zip(messages, labels):
        categorized.append({'category': int(label), 'text': msg})

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(orjson.dumps(categorized))

    print(f'Saved categorized messages to {output_path}')


if __name__ == '__main__':
    categorize_messages()
