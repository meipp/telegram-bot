from aiogram.types import Message
import numpy as np
import re

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


def parseXY(message: Message):
    x, y = [], []

    for line in message.text.splitlines():
        m = re.match(r'\A(.*):\s+(\d+)\Z', line)
        if not m:
            raise ValueError()
        x.append(m[1])
        y.append(int(m[2]))

    return x, y


def parseDict(message: Message):
    d = {}

    for line in message.text.splitlines():
        match = re.match(r"\A(.+):\s+(\d+)\Z", line)
        if not match:
            raise ValueError()

        d[match[1]] = int(match[2])
    return d


def parseMatrix(message: Message, delimiter: str = r"\s*[:\|\s]\s*"):
    matrix = []
    for line in message.text.splitlines():
        split_line = re.split(delimiter, line)
        matrix.append(split_line)

    return np.matrix(matrix)
