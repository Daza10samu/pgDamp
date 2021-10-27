import asyncio
from os import system
from pathlib import Path

from telethon import TelegramClient
from yaml import safe_load

current_dir = Path(__file__).parent.absolute()

with (current_dir / "config.yml").open() as stream:
    config = safe_load(stream)

bot = TelegramClient("bot", api_hash=config['main']['api_hash'], api_id=config['main']['api_id'])\
    .start(bot_token=config['main']['bot_token'])


system(
    f"docker exec {config['main']['docker_container']}"
    f" pg_dump -U {config['main']['db_name']}"
    f" --create > {current_dir}/dump.sql"
)


async def send_message(chat):
    with (current_dir / 'dump.sql').open("rb") as file:
        await bot.send_file(int(chat), file)


loop = asyncio.get_event_loop()
tasks = []

for chat in config["main"]["chats"]:
    tasks.append(loop.create_task(send_message(chat)))

loop.run_until_complete(asyncio.wait(tasks))
