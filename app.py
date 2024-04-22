from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import os
import subprocess

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
    url = " ".join(args)
    try:
        result = subprocess.run(["curl", url], capture_output=True, text=True)
        # check if error
        if result.returncode != 0:
            message.reply_text(TEMPLATE_CURL_ERROR.format(result.stderr))
            return

        message.reply_text(
            TEMPLATE_CURL_RESPONSE.format(
                "curl " + url,
                result.stdout[:3096],
                (
                    ("+ " + str(len(result.stdout[3096:])) + " more")
                    if len(result.stdout) > 3096
                    else ""
                ),
            )
        )
    except Exception as e:
        message.reply_text(TEMPLATE_CURL_ERROR.format(str(e)))


app.run()
