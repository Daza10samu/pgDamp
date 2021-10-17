from os import system
from pathlib import Path

from yaml import safe_load

from telebot import TeleBot

with Path("config.yaml").open() as stream:
    config = safe_load(stream)

bot = TeleBot(config["main"]["bot_token"])

system(
    f"PGPASSWORD={config['main']['db_pass']} pg_dump -U {config['main']['db_user']}"
    f"  --dbname=postgres --file='dump.sql' --create"
)

for chat in config["main"]["chats"]:
    with Path('dump.sql').open() as file:
        bot.send_document(chat, file)
