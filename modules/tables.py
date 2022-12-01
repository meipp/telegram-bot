from aiogram.types import Message

from bot.bot import on_reply, parseIndex
from bot.util import parseMatrix

@on_reply(command="submatrix")
async def command_submatrix(message: Message, *args):
    if len(args) >= 1:
        x1, x2, y1, y2 = parseIndex(args[0])

        matrix = parseMatrix(message)
        print(matrix)
        print(matrix[y1:y2, x1:x2])
