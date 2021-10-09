import logging
import os
import random
from typing import Optional, List

import markovify
from aiogram import Bot, Dispatcher, executor, types

import bloodbath
import asyncio
import aioschedule

logging.basicConfig(level=logging.DEBUG)

API_TOKEN: Optional[str] = os.getenv("BULLY_BOT_TOKEN")
DEFAULT_DATASET: List[str] = ["бебра", "иди мойся", "воняешь", "попу мыл?"]

bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher(bot)
dir_to_txt: str = "Dialogs/"


# MESSAGES
# ID TEXT FREQUENCY


async def startup(disp):
    print(disp)
    aioschedule.every().second.do(aboba)


def generate_message(chat_id: str) -> str:
    chat_path: str = f"{dir_to_txt}{chat_id}.txt"

    with open(chat_path, encoding="utf8") as file:
        lines = file.read()
        samples = (
            lines
            if lines.count("\n") >= 4
            else "\n".join(DEFAULT_DATASET)
        )

        generator: markovify.NewlineText = markovify.NewilineText(
            samples, state_size=1
        )

        sentence: str = generator.make_sentence(
            tries=100, min_words=1, test_output=random.random() < 0.6
        )
        return sentence


@dp.message_handler(content_types=["new_chat_members"])
async def new_chat(message: types.Message) -> None:
    dialog_filename: str = f"{dir_to_txt}{message.chat.id}.txt"
    if not os.path.exists(dialog_filename):
        open(dialog_filename, "w").close()
    for user in message.new_chat_members:
        if user.id == bot.id:
            await message.answer("ТОЛЯ, сделай меня админом!!!!!")


@dp.message_handler(commands=["start"], chat_type=types.ChatType.PRIVATE)
async def start(message: types.Message) -> None:
    await message.answer("Иди нахуй пидор.")


@dp.message_handler(commands=["help"])
async def react(message: types.Message) -> None:
    await message.answer(
        "\n".join(
            (
                "Мои команды:",
                "/gen - сгенерировать фразу",
                "/info - данные о базе",
            )
        )
    )


@dp.message_handler(commands=["gen"])
async def gen(message: types.Message) -> None:
    chat_id = message.chat.id

    await bot.delete_message(chat_id, message.message_id)
    await message.answer(
        generate_message(chat_id), disable_web_page_preview=True
    )


@dp.message_handler(commands=["info"])
async def info(message: types.Message) -> None:
    chat_path: str = f"{dir_to_txt}{message.chat.id}.txt"
    with open(chat_path, encoding="utf8") as f:
        text_count = len(f.readlines())
    await message.answer(
        "\n".join(
            (
                f"ID чата: {message.chat.id}",
                f"сохранено {text_count} строк"
            )
        )
    )


@dp.message_handler(content_types=["text"])
async def sov(message: types.Message) -> None:
    clean_message: str = bloodbath.sanitize(message.text)
    chat_path: str = f"{dir_to_txt}{message.chat.id}.txt"

    if bloodbath.valid(clean_message):
        with open(chat_path, "a", encoding="utf8") as f:
            f.write(message.text + "\n")

    is_reply = message.reply_to_message
    is_reply_to_bot = is_reply.from_user.is_bot if is_reply else False
    if random.randint(0, 6) == 0 or is_reply_to_bot:
        random_text = generate_message(message.chat.id)
        await message.reply(random_text, disable_web_page_preview=True)


def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(2, repeat, coro, loop)


if __name__ == "__main__":
    if not os.path.exists("Dialogs/"):
        os.mkdir("Dialogs/")


    async def aboba():
        pass


    loop = asyncio.get_event_loop()
    loop.call_later(2, repeat, aboba, loop)
    executor.start_polling(dp, skip_updates=True, loop=loop)
