import time
from utils import load_messages

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

messages = load_messages()


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/query/{query}")
async def read_item(query):
    query = query.lower()
    indices = []
    start = time.time()
    for i in range(len(messages)):
        text = str(messages[i]['text'])
        if query in text:
            indices.extend([messages[i]['id']])
    end = time.time()
    time_elapsed = end - start
    return {"results": indices, "count": len(indices), "time": time_elapsed}


@app.get("/search/{query}", response_class=HTMLResponse)
async def read_item(query):
    query = query.lower()
    indices = []
    start = time.time()
    for i in range(len(messages)):
        text = str(messages[i]['text'])
        if query in text:
            indices.extend([messages[i]['id']])
    end = time.time()
    time_elapsed = end - start
    html_content = ""
    for i in range(len(indices)):
        html_content += '<script>window.location="https://tx.me/s/rememberbox/{}"</script>'.format(indices[i])
    if not html_content:
        return "No results found!"
    return HTMLResponse(content=html_content, status_code=200)
