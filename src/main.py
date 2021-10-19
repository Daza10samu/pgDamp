from os import system
from pathlib import Path

from yaml import safe_load

from telebot import TeleBot

current_dir = Path(__file__).parent.absolute()

with (current_dir / "config.yml").open() as stream:
    config = safe_load(stream)

bot = TeleBot(config["main"]["bot_token"])

system(
    f"docker exec {config['main']['docker_container']}"
    f" pg_dump -U {config['main']['db_name']}"
    f" --create > {current_dir}/dump.sql"
)

for chat in config["main"]["chats"]:
    with (current_dir / 'dump.sql').open("rb") as file:
        bot.send_document(chat, file, timeout=config["main"]["timeout"])
