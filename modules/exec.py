from aiogram.types import Message
import os
from subprocess import Popen, PIPE, TimeoutExpired

from bot.bot import on, listen_on_change
from bot.util import parseArgs

whitelist = os.environ["EXEC_WHITELIST"].split(":")

@on(command="exec")
async def command_exec(message: Message, *_):
    print(message.from_user.first_name, message.from_user.id)
    if str(message.from_user.id) not in whitelist:
        raise RuntimeError("User is not whitelisted")

    async def exec(message: Message):
        args, kwargs = parseArgs(message)
        command = args
        timeout = 5

        p = Popen(command, stdout=PIPE, stderr=PIPE, encoding="utf-8")
        try:
            stdout, stderr = p.communicate(timeout=timeout)
        except TimeoutExpired:
            p.kill()
            raise TimeoutExpired(command, timeout)

        if p.returncode == 0:
            return stdout
        else:
            return f"status: {p.returncode}\nstdout: {stdout}\nstderr: {stderr}"


    await listen_on_change(message).then(exec).send()