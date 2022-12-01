from aiogram.types import ChatActions, Message
from subprocess import run

from bot.bot import on_reply, listen_on_change

@on_reply(command="silicon")
async def command_silicon(message: Message, *args):
    [language] = args
    command = ["silicon", "--language", language, "--output", "./silicon.png"]

    def render(message: Message):
        # await ChatActions.upload_photo()

        p = run(command, input=message.text, encoding="utf-8")
        if p.returncode != 0:
            raise RuntimeError()

        return {"photo": "./silicon.png"}

    await listen_on_change(message).then(render).send()
