from aiogram.types import ChatActions, Message
from subprocess import run

from bot.bot import on_reply, listen_on_change

def silicon(language: str = None, line_numbers: bool = False, window_controls: bool = True):
    command = ["silicon", "--output", "./silicon.png"]
    if language:
        command += ["--language", language]
    if not line_numbers:
        command += ["--no-line-number"]
    if not window_controls:
        command += ["--no-window-controls"]

    async def render(code: str):
        p = run(command, input=code, encoding="utf-8", timeout=5)
        if p.returncode != 0:
            raise RuntimeError()

        return {"photo": "./silicon.png"}

    return render


@on_reply(command="silicon")
async def command_silicon(message: Message, *args, **kwargs):
    language = args[0] if len(args) >= 1 else None
    line_numbers = kwargs.get("line-numbers") == "true"
    no_window_controls = kwargs.get("no-window-controls") == "true"

    await listen_on_change(message).then(lambda m: m.text).send(silicon(language, line_numbers, window_controls=not no_window_controls))
