"""Telegram bot interface for searching Remember Box messages."""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import timeit

from dotenv import load_dotenv
from pyrogram import Client, filters

from .utils import load_messages, list_builder

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

app = Client("user", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

messages = load_messages()


@app.on_message(filters.command(["start", "help"]))
def start(client, message):
    """Respond to start/help commands with a greeting."""
    message.reply('Hello, send me a query to search in @rememberbox!')


@app.on_message(filters.text)
def echo(client, message):
    """Search messages for the given text and return matching IDs."""
    text = message.text
    try:
        start_time = timeit.default_timer()
        indices = {messages[i]['id'] for i in range(len(messages)) if text in str(messages[i]['text'])}
        string = list_builder(list(indices))
        time_elapsed = (timeit.default_timer() - start_time) * 1000
        text = f"💡 Remember Box\n{string}\n{len(indices)} results in {time_elapsed:.2f} ms"
        message.reply(text)
    except Exception:
        message.reply("Query not found.")


logger.info("Ready to rock..!")
app.run()
