import time
from utils import load_messages
from search import SearchEngine, embedding_service

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

messages = load_messages()
search_engine = SearchEngine(embedding_service)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/query/{query}")
async def read_item(query: str, k: int = 5):
    """Return search results for query in JSON."""
    start = time.time()
    results = search_engine.search(query, k)
    time_elapsed = time.time() - start
    return {"results": results, "count": len(results), "time": time_elapsed}


@app.get("/search/{query}", response_class=HTMLResponse)
async def read_item_html(query: str, k: int = 5):
    """Redirect user to results on Telegram."""
    results = search_engine.search(query, k)
    if not results:
        return "No results found!"

    html_content = "".join(
        f'<script>window.open("https://t.me/c/1083858375/{rank}", "_blank")</script>'
        for rank, _, _ in results
    )
    return HTMLResponse(content=html_content, status_code=200)
