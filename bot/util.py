from aiogram.types import Message

def parseXY(message: Message):
    x, y = [], []

    for line in message.text.splitlines():
        m = re.match(r'\A(.*):\s+(\d+)\Z', line)
        if not m:
            raise ValueError()
        x.append(m[1])
        y.append(int(m[2]))

    return x, y

def parseMatrix(message: Message, delimiter: str = r"\s*[:\|]\s*"):
    matrix = []
    for line in message.text.splitlines():
        split_line = re.split(delimiter, line)
        matrix.append(split_line)

    return np.matrix(matrix)
