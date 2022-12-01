from aiogram.types import Message

from bot.bot import calculate_sum, on_reply, MessageListener, MessageSink, send_barplot

# competitions[chat_id][competition_name]
competitions = {}

class Competition:
    competition_name: str
    sink: MessageSink
    ranking: dict

    def __init__(self, competition_name: str):
        self.competition_name = competition_name
        self.sink = None
        self.ranking = {}

    async def add(self, message: Message):
        if not self.sink:
            self.sink = MessageSink(reply_to=message, answer_only=True, pin=True)

        async def helper(message: Message):
            sum = calculate_sum(message)
            name = message.from_user.first_name
            self.ranking[name] = sum
            await self.update()

        listener = MessageListener(message)
        listener.subscribe(helper)
        await listener.issue_update(message)

    async def update(self):
        x, y = self.ranking.keys(), self.ranking.values()
        await send_barplot(self.sink, x, y, title=self.competition_name)


@on_reply(command="compete")
async def command_compete(message: Message, *args, **kwargs):
    chat_id = message.chat.id
    competition_name = args[0] if len(args) >= 1 else "Competition"

    competition = competitions.setdefault(chat_id, {}).get(competition_name)
    if not competition:
        competition = Competition(competition_name)
        competitions[chat_id][competition_name] = competition
    await competition.add(message)
