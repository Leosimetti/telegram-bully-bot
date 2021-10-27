import logging
import os
import random
from datetime import datetime
from typing import Optional

import markovify
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType

import bloodbath

API_TOKEN: Optional[str] = os.getenv("BULLY_BOT_TOKEN")
NEAREST_ANIME_DATE = datetime(year=2021, month=10, day=30, hour=19)
ANIME_ROOM = 301

logging.basicConfig(level=logging.INFO)
bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher(bot)

dir_to_txt: str = "Dialogs/"


def generate_message(chat_id: str) -> str:
    chat_path: str = f"{dir_to_txt}{chat_id}.txt"

    with open(chat_path, encoding="utf8") as file:
        lines = file.read()
        if len(lines.splitlines()) >= 4:
            samples = lines
        else:
            samples = "\n".join(["бебра", "иди мойся", "воняешь", "попу мыл?"])

        generator: markovify.NewlineText = markovify.NewlineText(
            samples, state_size=1
        )

        sentence: str = generator.make_sentence(
            tries=100, min_words=1, test_output=random.random() < 0.6
        )

        # print("\n\n 🤡TEXT🤡 IS "+sentence+"\n\n")
        return sentence


def generate_sticker(chat_id: str) -> str:
    chat_path: str = f"{dir_to_txt}{chat_id}_stickers.txt"

    with open(chat_path, encoding="utf8") as file:
        stickers = file.read().splitlines()
        if len(stickers) <= 2:
            stickers = [
                "CAACAgIAAxkBAAIHEmFpignJ7aloUf0eh"
                "_vekLFEUq2nAAIUAAP6U-sWktE_IbXY9aYhBA"
            ]

        return random.choice(stickers)


async def get_time_to_anime(message, bypass=False):
    clean_message: str = bloodbath.sanitize(message.text)

    time_words = ["когда", "через", "сколько", "when"]
    anime_words = ["аниме", "онеме", "сходка", "сходочка", "anime"]
    msg = clean_message.lower()

    time_left = NEAREST_ANIME_DATE - datetime.now()
    if time_left.seconds > 0:
        has_anime = any(word in msg for word in anime_words)
        has_time = any(word in msg for word in time_words)
        has_gde = "где" in msg
        is_nice_message = has_anime and has_time
        is_place_message = has_gde and has_anime
        if is_place_message:
            await message.answer(f"Онеме будет в {ANIME_ROOM}")
        elif is_nice_message or bypass:

            times = (
                time_left.days,
                time_left.seconds // 3600,
                (time_left.seconds // 60) % 60,
                time_left.seconds % 60,
            )
            proper_times = zip(times, ["дней", "часов", "минут", "секунд"])
            answer = [
                f"{time[0]} {time[1]}" for time in proper_times if time[0] > 0
            ]
            await message.answer(
                f"До онеме сходОчки в {ANIME_ROOM} осталось {' '.join(answer)}"
            )
    else:
        await message.answer("Anime is no more...")
    return is_nice_message


@dp.message_handler(content_types=["new_chat_members"])
async def new_chat(message: types.Message) -> None:
    dialog_filename: str = f"{dir_to_txt}{message.chat.id}.txt"
    if not os.path.exists(dialog_filename):
        open(dialog_filename, "w").close()
    print("а кто")
    for user in message.new_chat_members:
        if user.id == bot.id:
            await message.answer("ТОЛЯ, сделай меня админом!!!!!")


@dp.message_handler(commands=["start"], chat_type=types.ChatType.PRIVATE)
async def start(message: types.Message) -> None:
    await message.answer("Иди найхуй пидор.")


@dp.message_handler(commands=["help"])
async def react(message: types.Message) -> None:
    await message.answer(
        "Мои команды:\n/gen - сгенерировать фразу\n/info - данные о базе"
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
        f"ID чата: {message.chat.id}\nсохранено {text_count} строк"
    )


@dp.message_handler(commands=["kogda"])
async def sxodka_time(message: types.message) -> None:
    chat_id = message.chat.id
    await bot.delete_message(chat_id, message.message_id)
    await get_time_to_anime(message, bypass=True)


@dp.message_handler(commands=["sticker"])
async def give_stick(message: types.message) -> None:
    chat_id = message.chat.id
    await bot.delete_message(chat_id, message.message_id)
    await message.answer_sticker(generate_sticker(chat_id=chat_id))


@dp.message_handler(content_types=ContentType.STICKER)
async def send_stick(message: types.Message) -> None:
    chat_path = f"{dir_to_txt}{message.chat.id}_stickers.txt"
    file_id = message.sticker.file_id
    with open(chat_path, "a", encoding="utf8") as f:
        f.write(file_id + "\n")

    is_reply = message.reply_to_message
    is_reply_to_bot = is_reply.from_user.is_bot if is_reply else False
    if random.randint(0, 3) == 0 or (is_reply_to_bot * random.randint(0, 1)):
        sticker = generate_sticker(chat_id=message.chat.id)
        if is_reply_to_bot:
            await message.reply_sticker(sticker)
        else:
            await message.answer_sticker(sticker)


@dp.message_handler(content_types=ContentType.TEXT)
async def sov(message: types.Message) -> None:
    clean_message: str = bloodbath.sanitize(message.text)
    chat_path = f"{dir_to_txt}{message.chat.id}.txt"

    if await get_time_to_anime(message):
        return

    if bloodbath.valid(clean_message):
        with open(chat_path, "a", encoding="utf8") as f:
            f.write(message.text + "\n")

    is_reply = message.reply_to_message
    is_reply_to_bot = is_reply.from_user.is_bot if is_reply else False
    if random.randint(0, 5) == 0 or is_reply_to_bot:

        if random.randint(0, 4) == 0:
            random_stick = generate_sticker(message.chat.id)
            await message.reply_sticker(random_stick)
        else:
            random_text = generate_message(message.chat.id)
            await message.reply(random_text, disable_web_page_preview=True)


if __name__ == "__main__":
    if not os.path.exists("Dialogs/"):
        os.mkdir("Dialogs/")
    executor.start_polling(dp, skip_updates=True)
