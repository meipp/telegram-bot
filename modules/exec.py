from aiogram.types import Message, User
import os
from subprocess import run, Popen, PIPE, TimeoutExpired

from bot.bot import on, listen_on_change
from bot.util import parseArgs

whitelist = os.environ["EXEC_WHITELIST"].split(":")


def authenticate(user: User):
    print("authenticate", user.first_name, user.username, user.id)
    if user.username not in whitelist and str(user.id) not in whitelist:
        raise RuntimeError("User is not whitelisted")

@on(command="exec")
async def command_exec(message: Message, *_):
    authenticate(message.from_user)

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

@on(command="shell")
async def command_shell(message: Message, *_):
    authenticate(message.from_user)

    async def exec(message: Message):
        args, kwargs = parseArgs(message)
        command = message.get_args()
        timeout = 5

        p = run(command, shell=True, capture_output=True, encoding="utf-8", timeout=timeout)

        if p.returncode == 0:
            return p.stdout
        else:
            return f"status: {p.returncode}\nstdout: {p.stdout}\nstderr: {p.stderr}"


    await listen_on_change(message).then(exec).send()
