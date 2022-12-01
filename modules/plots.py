from aiogram.types import Message

from bot.bot import on_reply, listen_on_change, bar, partialSums
from bot.util import parseXY

@on_reply(command="barplot")
async def command_barplot(message: Message):
    def barplot(message: Message):
        x, y = parseXY(message)
        return bar(x, y)

    await listen_on_change(message).send(barplot)

@on_reply(command="partialsums")
async def command_partialsums(message: Message):
    def partial_sum_plot(message: Message):
        x, y = parseXY(message)
        y = partialSums(y)
        return bar(x, y)

    await listen_on_change(message).then(partial_sum_plot).send()
