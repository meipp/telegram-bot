from aiogram.types import Message

from bot.bot import on_reply, parseIndex
from bot.util import parseMatrix

@on_reply(command="submatrix")
async def command_submatrix(message: Message, *args):
    if len(args) >= 1:
        x1, x2, y1, y2 = parseIndex(args[0])

        matrix = parseMatrix(message)
        submatrix = matrix[y1:y2, x1:x2]
        (yn, xn) = submatrix.shape

        s = ""
        for yi in range(yn):
            s += " ".join([submatrix[yi, xi] for xi in range(xn)]) + "\n"

        await message.reply(s)
