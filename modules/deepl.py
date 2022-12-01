from aiogram.types import ChatActions, Message
import deepl
import os

from bot.bot import on_reply, listen_on_change

DEEPL_API_KEY = os.environ["DEEPL_API_KEY"]

@on_reply(command="deepl")
async def command_deepl(message: Message, *args):
    [source_lang, target_lang] = args

    async def translation(message: Message):
        await ChatActions.typing()

        translator = deepl.Translator(DEEPL_API_KEY)
        result = translator.translate_text(message.text, source_lang=source_lang, target_lang=target_lang)
        translator.close()

        return result.text

    await listen_on_change(message).then(translation).send()
