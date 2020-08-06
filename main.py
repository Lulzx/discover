#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import logging
import simdjson
import time
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

with open('./result.json', 'rb') as fin:
    pj = simdjson.ParsedJson(fin.read())
    messages = pj.items('.chats.list[0].messages[]')


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


def start(update, context):
    update.message.reply_text('Hi!')


def help(update, context):
    update.message.reply_text('Help!')


def echo(update, context):
    indices = []
    text = update.message.text
    try:
        start = time.time()
        for i in range(len(messages)):
            if text in str(messages[i]['text']):
                scheme = messages[i]['id']
                if scheme not in indices:
                    indices.extend([scheme])
        # indices = list(dict.fromkeys(indices))
        string = list_builder(indices)
        end = time.time()
        time_elapsed = (end - start)*1000
        text = "💡 Remember Box\n" + string + "\n" + str(len(indices)) + " results in " + str(time_elapsed)[:5] + " milliseconds"
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except:
        update.message.reply_text("Query not found.")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    try:
        TOKEN = sys.argv[1]
    except IndexError:
        TOKEN = os.environ.get("TOKEN")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    logger.info("Ready to rock..!")
    updater.idle()


if __name__ == '__main__':
    main()