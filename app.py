from pyrogram import Client, filters
from pyrogram.types import Message
from templates import TEMPLATE_RESPONSE, TEMPLATE_ERROR
from dotenv import load_dotenv
import os
import subprocess
import shlex
import io
import time
import html
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


def process_command(commands, client: Client, message: Message, command_type):
    reply: Message = message.reply_text("Processing...")
    time_start = time.time()

    try:
        args = shlex.split(commands)
        result = subprocess.run(args, text=True, capture_output=True, errors="ignore")
        # check if error
        if result.returncode != 0:
            raise Exception(result.stderr)

        reply.edit_text(
            TEMPLATE_RESPONSE.format(
                input=html.escape(commands)[:512]
                + ("..." if len(commands) > 512 else ""),
                output=html.escape(result.stdout[:3096]),
                more=(
                    ("+ " + str(len(result.stdout[3096:])) + " more\n")
                    if len(result.stdout) > 3096
                    else ""
                ),
                done=time.time() - time_start,
            )
        )

        if len(result.stdout) > 3096:
            with io.BytesIO(str.encode(result.stdout)) as out_file:
                out_file.name = (
                    f"{command_type}_output_" + str(int(time.time())) + ".txt"
                )
                message.reply_document(out_file, reply_to_message_id=reply.id)

    except Exception as e:
        reply.edit_text(
            TEMPLATE_ERROR.format(
                input=html.escape(commands),
                output=html.escape(
                    str(e)[:3800] + ("..." if len(str(e)) > 3800 else "")
                )
                or "No output",
            )
        )


# incoming message private or group, starts with "curl <args>"
@app.on_message(
    filters.incoming
    & filters.create(
        lambda _, __, message: message.text and message.text.startswith("curl")
    )
)
def curl(client: Client, message: Message):
    commands = message.text
    process_command(commands, client, message, "curl")


# bash / shell command "! <args>"
@app.on_message(
    filters.incoming
    & filters.create(
        lambda _, __, message: message.text and message.text.startswith("!")
    )
)
def shell(client: Client, message: Message):
    commands = message.text[1:]
    process_command(commands, client, message, "shell")


app.run()
