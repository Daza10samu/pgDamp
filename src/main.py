from os import system
from pathlib import Path

from yaml import safe_load

from telebot import TeleBot

with Path("config.yml").open() as stream:
    config = safe_load(stream)

bot = TeleBot(config["main"]["bot_token"])

system(
    f"docker exec {config['main']['docker_container']}"
    f" pg_dump -U {config['main']['db_name']}"
    f" --create > dump.sql"
)

for chat in config["main"]["chats"]:
    with Path('dump.sql').open("rb") as file:
        bot.send_document(chat, file, timeout=config["main"]["timeout"])
