import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from aiogram.types.input_media import InputMediaPhoto
import re
import inspect
import os
import matplotlib.pyplot as plt

from bot.util import parseDict

API_TOKEN = os.environ["API_TOKEN"]

logging.basicConfig(level=logging.INFO)
plt.set_loglevel('WARNING')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)



def calculate_sum(message: Message):
    delimiter = r"\s*:\s+"

    sum = 0
    text = message.text
    for line in text.splitlines():
        columns = re.split(delimiter, line)
        sum += int(columns[1])

    return sum


# message_listeners[chat_id][message_id][i]
message_listeners = {}

available_commands = []

class MessagePipe:
    def __init__(self, f, x, root_message: Message):
        self.f = f
        self.x = x
        self.y = f(x)
        self.listeners = []
        self.root_message = root_message

    async def issue_update(self, x) -> None:
        self.x = x
        if inspect.iscoroutinefunction(self.f) or inspect.iscoroutine(self.f):
            self.y = await self.f(x)
        else:
            self.y = self.f(x)

        for listener in self.listeners:
            await listener(self.y)

    def subscribe(self, listener) -> None:
        self.listeners.append(listener)

    def then(self, g) -> "MessagePipe":
        downstream = MessagePipe(f=g, x=self.y, root_message=self.root_message)
        self.subscribe(downstream.issue_update)
        return downstream

    async def send(self, g = None, answer_only: bool = False, pin: bool = False):
        g = g if g else (lambda y: y)
        sink = MessageSink(reply_to=self.root_message, answer_only=answer_only, pin=pin)
        self.then(g).subscribe(sink.send)
        await self.issue_update(self.x)


class MessageListener(MessagePipe):
    def __init__(self, message: Message) -> None:
        super().__init__(f=(lambda x: x), x=message, root_message=message)

        add_message_listener(message.chat.id, message.message_id, self)

class MessageSink:
    def __init__(self, reply_to: Message = None, answer_only: bool = False, pin: bool = False) -> None:
        self.reply_to = reply_to
        self.answer_only = answer_only
        self.pin = pin
        self.message = None

    async def text(self, text: str) -> None:
        if not self.message:
            if self.answer_only:
                self.message = await self.reply_to.answer(text)
            else:
                self.message = await self.reply_to.reply(text)

            if self.pin:
                await self.message.pin()
        else:
            await self.message.edit_text(text)

    async def photo(self, photo: str, caption: str = None) -> None:
        if not self.message:
            if self.answer_only:
                self.message = await self.reply_to.answer_photo(open(photo, "rb"), caption=caption)
            else:
                self.message = await self.reply_to.reply_photo(open(photo, "rb"), caption=caption)

            if self.pin:
                await self.message.pin()
        else:
            await self.message.edit_media(media=InputMediaPhoto(open(photo, "rb"), caption=caption))

    async def send(self, data):
        if type(data) == str:
            await self.text(data)
        else:
            photo, caption = data.get("photo"), data.get("caption")
            await self.photo(photo, caption)

def listen_on_change(message: Message) -> MessageListener:
    return MessageListener(message)

def sumDict(d: dict) -> int:
    return sum(d.values())


def parseArgs(message: Message):
    args, kwargs = [], {}

    if message.get_args():
        for arg in re.split(r"\s+", message.get_args()):
            match = re.match(r"\A([^=]+)=([^=]+)\Z", arg)
            if match:
                kwargs[match[1]] = match[2]
            else:
                args.append(arg)

    return args, kwargs

def on(command: str, description: str = None, hidden: bool = False):
    def decorator(f):
        async def handler(message: Message):
            args, kwargs = parseArgs(message)
            return await f(message, *args, **kwargs)

        dp.message_handler(commands=[command])(handler)
        if not hidden:
            available_commands.append({"command": command, "description": description})
        return handler

    return decorator


def on_reply(command: str, description: str = None, hidden: bool = False):
    def decorator(f):
        async def handler(message: Message):
            if message.reply_to_message and message.reply_to_message.text:
                args, kwargs = parseArgs(message)
                return await f(message.reply_to_message, *args, **kwargs)

        dp.message_handler(commands=[command])(handler)
        if not hidden:
            available_commands.append({"command": command, "description": description})
        return handler

    return decorator


@dp.edited_message_handler()
async def message_edited(message: Message):
    for listener in message_listeners.get(message.chat.id, {}).get(message.message_id, []):
        await listener.issue_update(message)


def partialSums(y: list[int]):
    y2 = []
    sum = 0
    for n in y:
        sum += n
        y2.append(sum)

    return y2

def parseAlphabeticNumber(s: str):
    n = 0
    for c in s:
        n *= 26
        n += ord(c) - ord('A')
    return n

def parseIndex(index: str):
    m = re.match(r"\A([A-Z]+)(\d+):([A-Z]+)(\d+)\Z", index)
    if m:
        x1 = parseAlphabeticNumber(m[1])
        x2 = parseAlphabeticNumber(m[3]) + 1
        y1 = int(m[2]) - 1
        y2 = int(m[4]) - 1 + 1

    return x1, x2, y1, y2

async def send_barplot(sink: MessageSink, x: list[str], y: list[int], title: str = None, caption: str = None):
    plt.bar(x, y)
    plt.title(title)
    plt.savefig("./plot.png")
    plt.close()

    return await sink.photo(photo="./plot.png", caption=caption)

def bar(x: list[str], y: list[int], title: str = None, caption: str = None):
    plt.bar(x, y)
    plt.title(title)
    plt.savefig("./plot.png")
    plt.close()

    return {"photo": "./plot.png", "caption": caption}


def add_message_listener(chat_id, message_id, listener):
    message_listeners.setdefault(chat_id, {}).setdefault(message_id, []).append(listener)


@on_reply(command="sum")
async def command_sum(message: Message):
    await listen_on_change(message).then(parseDict).then(sumDict).then(lambda sum: f"Σ:{sum}").send()


@on(command="echo", hidden=True)
async def command_echo(message: Message, *args, **kwargs):
    await message.answer(f"args: {args}\nkwargs: {kwargs}")



@on(command="help", description="display this message")
async def command_help(message: Message):
    help = ""

    for c in available_commands:
        command, description = c.get("command"), c.get("description")

        help += f"/{command}"
        if description:
            help += f" - {description}"
        help += "\n"

    await message.answer(help)

def start_bot():
    executor.start_polling(dp, skip_updates=True)
