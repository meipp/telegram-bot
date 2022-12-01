from aiogram.types import Message
from datetime import datetime, timedelta

from bot.bot import on

started_at = datetime.now()

@on(command="uptime")
async def command_uptime(message: Message):
    uptime = datetime.now() - started_at
    uptime -= timedelta(microseconds=uptime.microseconds)
    await message.answer(f"uptime: {uptime}")
