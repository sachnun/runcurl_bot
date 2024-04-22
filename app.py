from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import os
import subprocess
import shlex

import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("bot_session", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# start command
@app.on_message(filters.command("start"))
def start(client: Client, message: Message):
    message.reply_text("Its working!")


TEMPLATE_CURL_RESPONSE = """
Input: 
```bash
{}
```
Output: 
```
{}
```
{}
"""


TEMPLATE_CURL_ERROR = """
Input: 
```bash
{}
```
Error: 
```
{}
```
"""


# curl command <args>
@app.on_message(filters.command("curl"))
def curl(client: Client, message: Message):
    args = message.text.split(" ")[1:]
    if len(args) == 0:
        message.reply_text("Usage: `/curl (args)`")
        return
    commands = "curl " + " ".join(args)

    try:
        args = shlex.split(commands)
        result = subprocess.run(
            args,
            text=True,
            capture_output=True,
        )
        # check if error
        if result.returncode != 0:
            raise Exception(result.stderr)

        message.reply_text(
            TEMPLATE_CURL_RESPONSE.format(
                commands,
                result.stdout[:3096],
                (
                    ("+ " + str(len(result.stdout[3096:])) + " more")
                    if len(result.stdout) > 3096
                    else ""
                ),
            )
        )
    except Exception as e:
        message.reply_text(TEMPLATE_CURL_ERROR.format(commands, e))


app.run()
